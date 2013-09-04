pytest-dbfixtures
=================

redis, mongo, rabbitmq py.test fixutres


Install
-------

::

    python setup.py install

How to use
----------

::

    def test_using_redis(redisdb):
        redisdb.set('woof', 'woof')
        redis.get('woof')

    def test_using_mongo(mongodb):
        mongodb.test.insert({'woof': 'woof'})
        mongodb.test.find_one()

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
