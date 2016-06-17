from pytest_dbfixtures import factories

dynamodb_proc = factories.dynamodb_proc(
    jar_path='/tmp/dynamodb/DynamoDBLocal.jar',
    host='localhost',
    port=8000
)
dynamodb = factories.dynamodb('dynamodb_proc')


def test_dynamodb(dynamodb):
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
