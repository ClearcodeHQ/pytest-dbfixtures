from path import path

from pytest_dbfixtures import factories


def test_mongo(mongodb):
    test_data = {
        "test1": "test1",
    }

    db = mongodb['test_db']
    db.test.insert(test_data)
    assert db.test.find_one()['test1'] == 'test1'


mongo_params = '--nojournal --noauth --nohttpinterface --noprealloc'

mongo_proc2 = factories.mongo_proc(port=27070, params=mongo_params)
mongodb2 = factories.mongodb('mongo_proc2')

mongo_proc3 = factories.mongo_proc(port=27071, params=mongo_params)
mongodb3 = factories.mongodb('mongo_proc3')


def test_third_mongo(mongodb, mongodb2, mongodb3):
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


def test_mongo_proc(mongo_proc, mongo_proc2, mongo_proc3):
    for m in (mongo_proc, mongo_proc2, mongo_proc3):
        assert path('/tmp/mongo.{port}.log'.format(port=m.port)).isfile()


mongo_proc_rand = factories.mongo_proc(port=None, params=mongo_params)
mongodb_rand = factories.mongodb('mongo_proc_rand')


def test_random_port(mongodb_rand):
    """Tests if mongo fixture can be started on random port"""
    server_info = mongodb_rand.server_info()
    assert 'ok' in server_info
    assert server_info['ok'] == 1.0
