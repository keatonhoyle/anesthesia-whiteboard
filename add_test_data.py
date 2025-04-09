import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Whiteboard')

# Add test data for Chippenham Hospital (hospital_id: 1)
table.put_item(
    Item={
        'Room': 'Room 1',
        'Provider': 'Dr. Smith',
        'Surgeon': 'Dr. Jones',
        'Staff': 'CRNA Johnson',
        'hospital_id': '1'
    }
)
table.put_item(
    Item={
        'Room': 'Room 2',
        'Provider': 'Dr. Lee',
        'Surgeon': 'Dr. Patel',
        'Staff': 'AA Davis',
        'hospital_id': '1'
    }
)

# Add test data for Johnston-Willis Hospital (hospital_id: 2)
table.put_item(
    Item={
        'Room': 'Room 3',
        'Provider': 'Dr. Wilson',
        'Surgeon': 'Dr. Taylor',
        'Staff': 'Student Miller',
        'hospital_id': '2'
    }
)

# Add test data for VCU Main Hospital (hospital_id: 3)
table.put_item(
    Item={
        'Room': 'Room 4',
        'Provider': 'Dr. Brown',
        'Surgeon': 'Dr. Clark',
        'Staff': 'CRNA Thompson',
        'hospital_id': '3'
    }
)

print("Test data added to DynamoDB.")