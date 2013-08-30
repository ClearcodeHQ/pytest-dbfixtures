pytest-dbfixtures
=================

Install
-------

    python setup.py install

How to use
----------

    def test_redis(redisdb):
        redisdb.set('woof', 'woof')

        redis.get('woof')

    def test_mongo(mongodb):
        mongodb.test.insert({'woof': 'woof'})
        mongodb.test.find_one()

Use your own configure files
----------------------------

Of course you can!

See examples configs:

    * pytest_dbfixtures/dbfixtures.conf
    * pytest_dbfixtures/redis.conf
    * pytest_dbfixtures/mongo.conf

If you want to use your own configs pass them as arguments to `py.test`.
Examples::

    py.test --dbfixtures-config my-dbfixtures.conf
    py.test --dbfixtures-config my-dbfixtures.conf --mongo-config
    my-mongo.conf
    py.test --redis-config my-redis.conf
