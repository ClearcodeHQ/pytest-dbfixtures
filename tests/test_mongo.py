from path import path

from pytest_dbfixtures import factories


def test_mongo(mongodb):
    assert path('/tmp/mongo.27069.log')

    test_data = {
        "test1": "test1",
    }

    db = mongodb['test_db']
    db.test.insert(test_data)
    assert db.test.find_one()['test1'] == 'test1'


mongo_proc2 = factories.mongo_proc(port=27070, params='--nojournal --noauth --nohttpinterface --noprealloc')
mongodb2 = factories.mongodb('mongo_proc2', port=27070)

mongo_proc3 = factories.mongo_proc(port=27071, params='--nojournal --noauth --nohttpinterface --noprealloc')
mongodb3 = factories.mongodb('mongo_proc3', port=27071)


def test_third_mongo(mongodb, mongodb2, mongodb3):
    for port in ('27069', '27070', '27071'):
        assert path('/tmp/mongo.{port}.log'.format(port=port))

    test_data_one = {
        "test1": "test1",
    }
    db = mongodb['test_db']
    db.test.insert(test_data_one)
    assert db.test.find_one()['test1'] == 'test1'

    test_data_two = {
        "test2": "test2",
    }
    db = mongodb2['test_db']
    db.test.insert(test_data_two)
    assert db.test.find_one()['test2'] == 'test2'

    test_data_three = {
        "test3": "test3",
    }
    db = mongodb3['test_db']
    db.test.insert(test_data_three)
    assert db.test.find_one()['test3'] == 'test3'
