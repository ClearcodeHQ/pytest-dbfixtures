import uuid


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
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    _id = str(uuid.uuid4())

    # put an item into db
    table.put_item(
        Item={
            'id': _id,
            'test_key': 'test_value'
        },
    )

    # get the item
    item = table.get_item(
        Key={
            'id': _id,
        }
    )

    # check the content of the item
    assert item['Item']['test_key'] == 'test_value'


def test_if_tables_does_not_exist(dynamodb):
    """
    We should clear this fixture (remove all tables).

    .. note::
        `all` method on tables object creates an iterable of all
        Table resources in the collection.
    """
    table_names = [t for t in dynamodb.tables.all()]
    assert len(table_names) == 0
