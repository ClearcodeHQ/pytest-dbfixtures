.. _configure:

Use your own configure files
============================

Below you can see example configs.

* pytest_dbfixtures/dbfixtures.conf
* pytest_dbfixtures/redis.conf
* pytest_dbfixtures/rabbit.conf

If you want to use your own configs pass them as arguments to ``py.test`` command.

.. sourcecode:: bash

    $ py.test --dbfixtures-config my-dbfixtures.conf

    $ py.test --dbfixtures-config my-dbfixtures.conf --redis-config my-redis.conf

    $ py.test --redis-config my-redis.conf

    $ py.test --rabbit-config my-rabbit.conf