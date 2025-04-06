from django.shortcuts import render
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Whiteboard')

def home(request):
    # Fetch data from DynamoDB
    try:
        response = table.scan()
        items = response.get('Items', [])
        # Convert DynamoDB items to the same format as the in-memory dictionary
        whiteboard = {}
        for item in items:
            room = item['Room']
            whiteboard[room] = {
                'provider': item.get('Provider', ''),
                'surgeon': item.get('Surgeon', '')
            }
    except Exception as e:
        print(f"Error fetching data from DynamoDB: {e}")
        # Fallback to in-memory data if DynamoDB fails
        whiteboard = {
            "Room 1": {"provider": "Dr. Smith", "surgeon": "Dr. Jones"},
            "Room 2": {"provider": "Dr. Lee", "surgeon": "Dr. Patel"}
        }
    return render(request, 'index.html', {'whiteboard': whiteboard})