pytest-dbfixtures
=================

py.test clean fixtures: mysql, redis, mongo, rabbitmq

Starts specific database deamon and cleanup all data produced during tests.


Install
-------

.. sourcecode:: bash

    $ pip install pytest-dbfixtures


How to use
----------

.. sourcecode:: python

    def test_using_mysql(mysqldb):
        mysqldb.query("SELECT CURRENT_USER()")


    @pytest.fixture(scope='session')
    def some_session_fixture(mysqldb_session):
        mysqldb_session.query("CREATE DATABASE xyz")
        rows = mysqldb_session.query("USE xyz")


    def test_using_redis(redisdb):
        redisdb.set('woof', 'woof')
        woof = redisdb.get('woof')


    def test_using_mongo(mongodb):
        db = mongodb['test_database']
        db.test.insert({'woof': 'woof'})
        documents = db.test.find_one()


    def test_using_rabbit(rabbitmq):
        channel = rabbitmq.channel()


Use your own configure files
----------------------------

Of course you can! Below you can see example configs.

* pytest_dbfixtures/dbfixtures.conf
* pytest_dbfixtures/redis.conf
* pytest_dbfixtures/mongo.conf
* pytest_dbfixtures/rabbit.conf

If you want to use your own configs pass them as arguments to `py.test`.

Examples::

    py.test --dbfixtures-config my-dbfixtures.conf

    py.test --dbfixtures-config my-dbfixtures.conf --mongo-config my-mongo.conf

    py.test --redis-config my-redis.conf
    py.test --rabbit-config my-rabbit.conf
