from django.shortcuts import render, redirect
import boto3
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, Division, Hospital

# Set up logging
logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Whiteboard')

def fetch_whiteboard_data():
    try:
        response = table.scan()
        items = response.get('Items', [])
        whiteboard = {}
        for item in items:
            if 'Room' not in item:
                logger.warning(f"Item missing Room attribute: {item}")
                continue
            room = item['Room']
            provider = item.get('Provider') or item.get('provider') or item.get('provider_name', '')
            surgeon = item.get('Surgeon') or item.get('surgeon') or item.get('surgeon_name', '')
            whiteboard[room] = {
                'provider': provider,
                'surgeon': surgeon
            }
            if not provider or not surgeon:
                logger.warning(f"Missing provider or surgeon for room {room}: {item}")
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
            return redirect('select_division')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def select_division(request):
    user = request.user
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
    selected_hospital_id = request.session.get('selected_hospital_id')
    if not selected_hospital_id:
        return redirect('select_hospital')

    whiteboard = fetch_whiteboard_data()
    if whiteboard is None:
        messages.error(request, "Failed to load whiteboard data from DynamoDB. Please check your AWS credentials and try again.")
        whiteboard = {
            "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones"},
            "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel"}
        }
    return render(request, 'index.html', {'whiteboard': whiteboard})

@login_required
def edit_entry(request, room):
    if request.method == 'POST':
        provider = request.POST.get('provider')
        surgeon = request.POST.get('surgeon')
        try:
            table.update_item(
                Key={'Room': room},
                UpdateExpression="SET Provider = :p, Surgeon = :s",
                ExpressionAttributeValues={
                    ':p': provider,
                    ':s': surgeon
                }
            )
            messages.success(request, f"Updated {room} successfully!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error updating {room}: {str(e)}")
            return redirect('home')

    # Fetch the entry to edit
    try:
        response = table.get_item(Key={'Room': room})
        entry = response.get('Item')
        if not entry:
            messages.error(request, f"Room {room} not found in DynamoDB.")
            return redirect('home')
    except Exception as e:
        messages.error(request, f"Error fetching {room}: {str(e)}")
        return redirect('home')

    return render(request, 'edit.html', {'entry': entry})

@login_required
def add_entry(request):
    if request.method == 'POST':
        room = request.POST.get('room')
        provider = request.POST.get('provider')
        surgeon = request.POST.get('surgeon')

        try:
            # Check if the room already exists
            response = table.get_item(Key={'Room': room})
            if response.get('Item'):
                messages.error(request, f"Room {room} already exists!")
                return redirect('home')

            # Add the new entry
            table.put_item(
                Item={
                    'Room': room,
                    'Provider': provider,
                    'Surgeon': surgeon
                }
            )
            messages.success(request, f"Added {room} successfully!")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"Error adding {room}: {str(e)}")
            return redirect('home')

    return render(request, 'add.html')

def logout_view(request):
    logout(request)
    return redirect('login')