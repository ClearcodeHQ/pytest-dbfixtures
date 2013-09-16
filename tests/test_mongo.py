def test_mongo(mongodb):
    test_data = {
        "test1": "test1",
    }

    db = mongodb['test_db']
    db.test.insert(test_data)
    assert db.test.find_one()['test1'] == 'test1'
