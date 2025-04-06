from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import boto3
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Whiteboard')

@login_required
def home(request):
    # Fetch data from DynamoDB
    try:
        response = table.scan()
        items = response.get('Items', [])
        # Convert DynamoDB items to the expected format
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
    except Exception as e:
        logger.error(f"Error fetching data from DynamoDB: {e}")
        whiteboard = {
            "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones"},
            "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel"}
        }
    return render(request, 'index.html', {'whiteboard': whiteboard})