from django.shortcuts import render, redirect
import boto3
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, Division, Hospital
import os
import uuid
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

from django.conf import settings

# Initialize DynamoDB client
dynamodb_endpoint = os.getenv('DYNAMODB_ENDPOINT', 'http://localhost:8000')
dynamodb = boto3.resource(
    'dynamodb',
    region_name='us-east-1',
    endpoint_url=dynamodb_endpoint,
    aws_access_key_id='fakeMyKeyId',
    aws_secret_access_key='fakeSecretAccessKey'
)
whiteboard_table = dynamodb.Table(settings.WHITEBOARD_TABLE)
staff_table = dynamodb.Table(settings.STAFF_TABLE)
assignments_table = dynamodb.Table(settings.ROOM_ASSIGNMENTS_TABLE)

def fetch_staff():
    try:
        response = staff_table.scan()
        items = response.get('Items', [])
        logger.info(f"Fetched {len(items)} staff members: {items}")
        return items
    except Exception as e:
        logger.error(f"Error fetching staff from DynamoDB: {e}")
        return []

def fetch_whiteboard_data(hospital_id=None):
    try:
        response = whiteboard_table.scan()
        items = response.get('Items', [])
        logger.info(f"Raw whiteboard items: {items}")
        # Fetch staff list to map staff_id to name and role
        staff_list = fetch_staff()
        staff_dict = {staff['staff_id']: staff for staff in staff_list}
        whiteboard = {}
        for item in items:
            if 'Room' not in item:
                logger.warning(f"Item missing Room attribute: {item}")
                continue
            # Filter by hospital_id if provided
            if hospital_id and item.get('hospital_id') != str(hospital_id):
                continue
            room = item['Room']
            provider = item.get('Provider') or item.get('provider') or item.get('provider_name', '')
            surgeon = item.get('Surgeon') or item.get('surgeon') or item.get('surgeon_name', '')
            staff_id = item.get('Staff', '')
            # Map staff_id to staff name and role
            staff_info = staff_dict.get(staff_id, {'name': f"Unknown (staff_id: {staff_id})", 'role': ''})
            whiteboard[room] = {
                'provider': provider,
                'surgeon': surgeon,
                'staff_id': staff_id,
                'staff_name': staff_info['name'],
                'staff_role': staff_info['role']
            }
            if not provider or not surgeon:
                logger.warning(f"Missing provider or surgeon for room {room}: {item}")
        logger.info(f"Processed whiteboard data: {whiteboard}")
        return whiteboard
    except Exception as e:
        logger.error(f"Error fetching data from DynamoDB: {e}")
        return None

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'admin':
                return redirect('/admin/')
            return redirect('select_division')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def select_division(request):
    user = request.user
    if user.role == 'admin':
        return redirect('/admin/')

    assigned_divisions = user.assigned_divisions.all()
    if not assigned_divisions:
        messages.error(request, "You are not assigned to any divisions. Please contact an admin.")
        return redirect('home')

    if len(assigned_divisions) == 1:
        # If only one division, auto-select it
        request.session['selected_division_id'] = assigned_divisions[0].id
        return redirect('select_hospital')

    if request.method == 'POST':
        selected_division_id = request.POST.get('division')
        try:
            selected_division = assigned_divisions.get(id=selected_division_id)
            request.session['selected_division_id'] = selected_division.id
            return redirect('select_hospital')
        except Division.DoesNotExist:
            messages.error(request, "Invalid division selection.")
            return redirect('select_division')

    return render(request, 'select_division.html', {'divisions': assigned_divisions})

@login_required
def select_hospital(request):
    user = request.user
    if user.role == 'admin':
        return redirect('/admin/')

    selected_division_id = request.session.get('selected_division_id')
    if not selected_division_id:
        return redirect('select_division')

    try:
        selected_division = Division.objects.get(id=selected_division_id)
    except Division.DoesNotExist:
        messages.error(request, "Invalid division selected.")
        return redirect('select_division')

    hospitals = selected_division.hospitals.all()
    if not hospitals:
        messages.error(request, "No hospitals available in this division.")
        return redirect('home')

    if len(hospitals) == 1:
        # If only one hospital, auto-select it
        request.session['selected_hospital_id'] = hospitals[0].id
        return redirect('home')

    if request.method == 'POST':
        selected_hospital_id = request.POST.get('hospital')
        try:
            selected_hospital = hospitals.get(id=selected_hospital_id)
            request.session['selected_hospital_id'] = selected_hospital.id
            return redirect('home')
        except Hospital.DoesNotExist:
            messages.error(request, "Invalid hospital selection.")
            return redirect('select_hospital')

    return render(request, 'select_hospital.html', {'hospitals': hospitals})

@login_required
def home(request):
    user = request.user
    if user.role == 'admin':
        return redirect('/admin/')

    selected_hospital_id = request.session.get('selected_hospital_id')
    if not selected_hospital_id:
        return redirect('select_hospital')

    whiteboard = fetch_whiteboard_data(hospital_id=selected_hospital_id)
    if whiteboard is None:
        messages.error(request, "Failed to load whiteboard data from DynamoDB. Please check your AWS credentials and try again.")
        whiteboard = {
            "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones", "staff_id": "1", "staff_name": "CRNA Johnson", "staff_role": "CRNA"},
            "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel", "staff_id": "2", "staff_name": "AA Davis", "staff_role": "AA"}
        }
    staff_list = fetch_staff()
    if not staff_list:
        messages.warning(request, "No staff members found in the database.")
    logger.info(f"Whiteboard data: {whiteboard}")
    logger.info(f"Staff list in home view: {staff_list}")
    return render(request, 'index.html', {'whiteboard': whiteboard, 'staff_list': staff_list})

@login_required
def edit_entry(request, room):
    selected_hospital_id = request.session.get('selected_hospital_id')
    if not selected_hospital_id:
        return redirect('select_hospital')

    staff_list = fetch_staff()

    if request.method == 'POST':
        provider = request.POST.get('provider')
        surgeon = request.POST.get('surgeon')
        staff_id = request.POST.get('staff')
        try:
            # Update the whiteboard entry
            whiteboard_table.update_item(
                Key={'Room': room},
                UpdateExpression="SET Provider = :p, Surgeon = :s, Staff = :st, hospital_id = :h",
                ExpressionAttributeValues={
                    ':p': provider,
                    ':s': surgeon,
                    ':st': staff_id,
                    ':h': str(selected_hospital_id)
                }
            )
            # Log the assignment in RoomAssignments
            assignment_id = str(uuid.uuid4())
            assignment_date = datetime.now().strftime('%Y-%m-%d')
            assignments_table.put_item(
                Item={
                    'assignment_id': assignment_id,
                    'room': room,
                    'hospital_id': str(selected_hospital_id),
                    'surgeon_id': surgeon,  # For now, using name; we'll update to IDs later
                    'anesthesiologist_id': provider,  # For now, using name
                    'app_id': staff_id,
                    'student_id': staff_id if any(staff['staff_id'] == staff_id and staff['sub_role'] == 'SRNA' for staff in staff_list) else '',
                    'date': assignment_date,
                    'cases': [],  # Placeholder for cases
                    'provider_mode': 'Directed CRNA' if any(staff['staff_id'] == staff_id and staff['role'] == 'CRNA' for staff in staff_list) else 'Directed AA'
                }
            )
            messages.success(request, f"Updated {room} successfully!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error updating {room}: {str(e)}")
            return redirect('home')

    # Fetch the entry to edit
    try:
        response = whiteboard_table.get_item(Key={'Room': room})
        entry = response.get('Item')
        if not entry or entry.get('hospital_id') != str(selected_hospital_id):
            messages.error(request, f"Room {room} not found in this hospital.")
            return redirect('home')
    except Exception as e:
        messages.error(request, f"Error fetching {room}: {str(e)}")
        return redirect('home')

    return render(request, 'edit.html', {'entry': entry, 'staff_list': staff_list})

@login_required
def add_entry(request):
    selected_hospital_id = request.session.get('selected_hospital_id')
    if not selected_hospital_id:
        return redirect('select_hospital')

    staff_list = fetch_staff()

    if request.method == 'POST':
        room = request.POST.get('room')
        provider = request.POST.get('provider')
        surgeon = request.POST.get('surgeon')
        staff_id = request.POST.get('staff')

        try:
            # Check if the room already exists
            response = whiteboard_table.get_item(Key={'Room': room})
            if response.get('Item'):
                messages.error(request, f"Room {room} already exists!")
                return redirect('home')

            # Add the new entry with hospital_id and staff
            whiteboard_table.put_item(
                Item={
                    'Room': room,
                    'Provider': provider,
                    'Surgeon': surgeon,
                    'Staff': staff_id,
                    'hospital_id': str(selected_hospital_id)
                }
            )
            # Log the assignment in RoomAssignments
            assignment_id = str(uuid.uuid4())
            assignment_date = datetime.now().strftime('%Y-%m-%d')
            assignments_table.put_item(
                Item={
                    'assignment_id': assignment_id,
                    'room': room,
                    'hospital_id': str(selected_hospital_id),
                    'surgeon_id': surgeon,  # For now, using name; we'll update to IDs later
                    'anesthesiologist_id': provider,  # For now, using name
                    'app_id': staff_id,
                    'student_id': staff_id if any(staff['staff_id'] == staff_id and staff['sub_role'] == 'SRNA' for staff in staff_list) else '',
                    'date': assignment_date,
                    'cases': [],  # Placeholder for cases
                    'provider_mode': 'Directed CRNA' if any(staff['staff_id'] == staff_id and staff['role'] == 'CRNA' for staff in staff_list) else 'Directed AA'
                }
            )
            messages.success(request, f"Added {room} successfully!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error adding {room}: {str(e)}")
            return redirect('home')

    return render(request, 'add.html', {'staff_list': staff_list})

def logout_view(request):
    logout(request)
    return redirect('login')