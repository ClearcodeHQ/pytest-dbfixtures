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


Use your custom path for logs
=============================

You can collect logs from all databases in a custom path by passing ``--dbfixtures-logsdir`` argument to ``py.test`` command.

.. sourcecode:: bash

    $ py.test --dbfixtures-logsdir /my/custom/path


Custom prefix for log file of log directory
-------------------------------------------

Additionaly you can add prefix to log file or log directory for each database fixture. Just pass the ``logs_prefix`` argument.

Example:

.. sourcecode:: python

    mysql_proc = factories.mysql_proc(port=3308, logs_prefix='myproject-')
