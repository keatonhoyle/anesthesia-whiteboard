import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url='http://localhost:8000')
table = dynamodb.Table('Whiteboard-Dev')

# Add test data for Chippenham Hospital (hospital_id: 1)
table.put_item(
    Item={
        'Room': 'Room 1',
        'Provider': 'Dr. Smith',
        'Surgeon': 'Dr. Jones',
        'Staff': '1',  # staff_id for CRNA Johnson
        'hospital_id': '1'
    }
)
table.put_item(
    Item={
        'Room': 'Room 2',
        'Provider': 'Dr. Lee',
        'Surgeon': 'Dr. Patel',
        'Staff': '2',  # staff_id for AA Davis
        'hospital_id': '1'
    }
)

# Add test data for Johnston-Willis Hospital (hospital_id: 2)
table.put_item(
    Item={
        'Room': 'Room 3',
        'Provider': 'Dr. Wilson',
        'Surgeon': 'Dr. Taylor',
        'Staff': '3',  # staff_id for Student Miller
        'hospital_id': '2'
    }
)

# Add test data for VCU Main Hospital (hospital_id: 3)
table.put_item(
    Item={
        'Room': 'Room 4',
        'Provider': 'Dr. Brown',
        'Surgeon': 'Dr. Clark',
        'Staff': '4',  # staff_id for CRNA Thompson
        'hospital_id': '3'
    }
)

print("Test data updated in DynamoDB.")