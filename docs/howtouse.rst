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

MySQL
-----

.. sourcecode:: python

    def test_using_mysql(mysqldb):
        mysqldb.query("SELECT CURRENT_USER()")


    @pytest.fixture(scope='session')
    def some_session_fixture(mysqldb_session):
        mysqldb_session.query("CREATE DATABASE xyz")
        rows = mysqldb_session.query("USE xyz")



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
