from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import boto3
import logging

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
        return {
            "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones"},
            "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel"}
        }

@login_required
def home(request):
    # Check user group
    user_groups = request.user.groups.values_list('name', flat=True)
    if 'Admin' in user_groups:
        role = 'Admin'
    elif 'Manager' in user_groups:
        role = 'Manager'
    elif 'User' in user_groups:
        role = 'User'
    else:
        role = 'None'

    # Fetch whiteboard data
    whiteboard = fetch_whiteboard_data()

    # Pass role to template for display
    return render(request, 'index.html', {'whiteboard': whiteboard, 'role': role})

def custom_logout(request):
    logger.info("Logging out user: %s", request.user)
    logout(request)
    logger.info("User logged out, redirecting to /login/")
    return redirect('/login/')