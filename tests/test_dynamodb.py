from pytest_dbfixtures import factories

dynamodb_proc = factories.dynamodb_proc(
    jar_path='/tmp/dynamodb/DynamoDBLocal.jar'
)
dynamodb = factories.dynamodb('dynamodb_proc')

dynamodb_proc_random_port = factories.dynamodb_proc(
    jar_path='/tmp/dynamodb/DynamoDBLocal.jar',
    port='?',
)
dynamodb_random_port = factories.dynamodb('dynamodb_proc_random_port')


def test_dynamodb(dynamodb):
    """
    Simple test for DynamoDB.

    # Create a table
    # Put an item
    # Get the item and check the content of this item
    """
    # create a table
    table = dynamodb.create_table(
        TableName='Test',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'data',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'data',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    _id = 89734943
    data = "test1 test2 test3"

    # put an item into db
    table.put_item(
        Item={
            'id': _id,
            'data': data,
            'test_key': 'test_value'
        }
    )

    # get the item
    item = table.get_item(
        Key={
            'id': _id,
            'data': data,
        }
    )

    # check the content of the item
    assert item['Item']['test_key'] == 'test_value'


def test_dynamodb_random_port(dynamodb_random_port):
    """
    Test random port for DynamoDB.

    # Create a table
    # Put an item
    # Get the item and check the content of this item
    """
    # create a table
    table = dynamodb_random_port.create_table(
        TableName='Test',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            }

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    _id = 1111111

    # put an item into db
    table.put_item(
        Item={
            'id': _id,
            'test_key': 'test_value'
        }
    )

    # get the item
    item = table.get_item(
        Key={
            'id': _id,
        }
    )

    # check the content of the item
    assert item['Item']['test_key'] == 'test_value'
