def test_mongo(mongodb):
    test_data = {
        "test1": "test1",
    }

    mongodb.test.insert(test_data)
    assert mongodb.test.find_one()['test1'] == 'test1'
