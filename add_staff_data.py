import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url='http://localhost:8000')
table = dynamodb.Table('Staff-Dev')

# Add test staff members
table.put_item(
    Item={
        'staff_id': '1',
        'name': 'CRNA Johnson',
        'role': 'CRNA',
        'sub_role': '',
        'location_id': '1'  # Chippenham Hospital
    }
)
table.put_item(
    Item={
        'staff_id': '2',
        'name': 'AA Davis',
        'role': 'AA',
        'sub_role': '',
        'location_id': '1'  # Chippenham Hospital
    }
)
table.put_item(
    Item={
        'staff_id': '3',
        'name': 'Student Miller',
        'role': 'Student',
        'sub_role': 'SRNA',
        'location_id': '2'  # Johnston-Willis Hospital
    }
)
table.put_item(
    Item={
        'staff_id': '4',
        'name': 'CRNA Thompson',
        'role': 'CRNA',
        'sub_role': '',
        'location_id': '3'  # VCU Main Hospital
    }
)

print("Test staff data added to DynamoDB.")