from django.shortcuts import render, redirect
import boto3
import logging
from django.contrib import messages

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

def home(request):
    whiteboard = fetch_whiteboard_data()
    if whiteboard is None:
        messages.error(request, "Failed to load whiteboard data from DynamoDB. Please check your AWS credentials and try again.")
        whiteboard = {
            "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones"},
            "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel"}
        }
    return render(request, 'index.html', {'whiteboard': whiteboard})

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