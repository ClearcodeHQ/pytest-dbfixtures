.. _howtouse:


How to use
==========

Mongo
-----

.. sourcecode:: python

    def test_using_mongo(mongodb):
        db = mongodb['test_database']
        db.test.insert({'woof': 'woof'})
        documents = db.test.find_one()


    from pytest_dbfixtures import factories
    mongo_proc2 = factories.mongo_proc(port=27070)
    mongodb2 = factories.mongodb('mongo_proc2', port=27070)

    def test_second_mongo(mongodb, mongodb2, mongodb3):
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

MySQL
-----

.. sourcecode:: python

    def test_using_mysql(mysqldb):
        mysqldb.query("SELECT CURRENT_USER()")


    @pytest.fixture(scope='session')
    def some_session_fixture(mysqldb_session):
        mysqldb_session.query("CREATE DATABASE xyz")
        rows = mysqldb_session.query("USE xyz")

    # second database
    from pytest_dbfixtures import factories

    query = '''CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20),
    species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);'''

    mysql_proc2 = factories.mysql_proc(port=3308, params='--skip-sync-frm')
    mysqldb2 = factories.mysqldb('mysql_proc2', port=3308)

    def test_mysql_newfixture(mysqldb, mysqldb2):
        cursor = mysqldb.cursor()
        cursor.execute(query)
        mysqldb.commit()
        cursor.close()

        cursor = mysqldb2.cursor()
        cursor.execute(query)
        mysqldb2.commit()
        cursor.close()


Rabbit
------

.. sourcecode:: python

    def test_using_rabbit(rabbitmq):
        channel = rabbitmq.channel()

Redis
-----

.. sourcecode:: python

    def test_using_redis(redisdb):
        redisdb.set('woof', 'woof')
        woof = redisdb.get('woof')

    from pytest_dbfixtures import factories

    redis_proc2 = factories.redis_proc(port=6381)
    redisdb2 = factories.redisdb('redis_proc2', port=6381)

    def test_using_two_redis(redisdb, redisdb2):
        redisdb.set('woof1', 'woof1')
        redisdb2.set('woof2', 'woof12')

        woof1 = redisdb.get('woof1')
        woof2 = redisdb2.get('woof2')
