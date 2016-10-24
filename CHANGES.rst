CHANGES
=======

0.17.0
------

- [enhancement] split out PostgreSQL fixtures into separate package. See `pytest-postgresql <https://pypi.python.org/pypi/pytest-postgresql/>`_
- [enhancement] split out MongoDB fixtures into separate package. See `pytest-mongo <https://pypi.python.org/pypi/pytest-mongo/>`_

0.16.0
------

- [enhancements] Postgresql client fixture closes other postgresql connection to the database before droping database - prevents the fixture/tests from hanging in some cases
- [enhancements] mysql to use unique tmpdir option for mysql_* commands
- [enhancements] use semicolon to terminate postgresql CREATE/DROP DATABASE statements
- [bugfix] removed unneded dependency
- [enhancement] split out elasticsearch fixtures into separate package. See `pytest-elasticsearch <https://pypi.python.org/pypi/pytest-elasticsearch/>`_
- [feature] use tmpfile.gettempdir instead of hardcoded /tmp directory

0.15.0
------

- [fix] support for rabbitpy 0.27.x
- [feature] Random port selection ports accept tuples and sets. replace string representation [backward incompatible]


0.14.3
------

- [feature] Add support for delayTransientStatuses flag (DynamoDB)

0.14.2
------

- [fix] Update DynamoDB in howtouse

0.14.1
------

- [fix] packaging/changelog fix

0.14.0
------

- [feature] add fixture for DynamoDB

0.13.1
------

- [bugfix] fix dbfixtures packaging

0.13.0
------

- [feature] make it easier to support future postgresql out of the box
- [feature] support for postgresql 9.5
- [docs] add contribute guidelines
- [feature] add info about minimal version supported - closes #132
- [enhancements] - moved source code into src folder
- [feature] python3.5 compatibility
- [docs] enhance docs - refs #126
- [feature]  PGsql connection error on FreeBSD jailed environments

    In FreeBSD jailed environments the loopback interface can not be used to
    connect to pgsql, because it points to the loopback interface of the host and
    not the jail.

    Thus, it seems to pgsql like the connection is comming from the ip address
    assigned to the jail.

    This ensures that pgsql can be connected to from any host, when
    run on a FreeBSD systems. This this package can be used in FreeBSD
    jailed environments

- [feature] Use log destination param for pgsql

    This commit ensures that `stderr` is used for logging, by
    specifying the command line parameter.

    On FreeBSD this is very important otherwise syslog will be used and
    the db-fixtures will hang as it looks in the expected log file and
    loops forever waiting for a "database is ready" entry to appear...
    `log_destination=stderr` is default on most systems and can be set in
    `postgresql.conf` or given as an command line argument.

    `Read more <http://www.postgresql.org/docs/9.1/static/runtime-config-logging.html>`_

0.12.0
------

- [bugfix] mongodb fixture no longer removes any of system.* collections
- [bugfix] configured pytest-dbfixtures to work with pymlconf versions compatible with Python 3

0.11.0
------

- make pytest-dbfixtures compatible with mirakuru 0.5.0


0.10.0
------

- fix W503 pep8 errors, that appeared after new pylama got released
- update to be able to use pytest-dbfixtures with pymongo 3
- ability to properly use also beta versions of postgresql releases. (previously only stable versions were targeted)


0.9.0
-----

- add ability to set custom location for logs (might be useful for analysing logs from tests)
- added postgresql 9.4 to supported versions.

0.8.2
-----

- Use port number in default RabbitMQ node name.

    This allows using just the port='?' argument to rabbitmq_proc to run multiple
    independent RabbitMQ instances for use with xdist to parallelize tests on a
    single machine.

- Old versions of Redis notification

    displays a message about old version of redis

0.8.1
-----

- Feature: random ports selection
  Adds a possibility of passing '?' in port= argument of process fixtures.
- Removes 'port' from db fixtures
- Fixes postgres missing host - previously using config.postgresql.unixsocketdir


0.7.0
-----

- redisdb fixture allows to specify client connection class
- redisdb fixture uses now StrictRedis by default (backward incompatible)

0.6.0
-----

- replaced *MySQLdb* with it's fork *mysqlclient* - compatibility with python3
- renamed mysqldb fixture to mysql to keep it consistent with other client fixtures.
- replaced *pika* with python 3 compatible rabbitpy
- removed deprecated mysqldb_session/mysql_session
- bugfix of rabbitmq fixture: cast rabbitmq queues and exchanges to str due to pamq having problems
- internal changes: removed GentleKillingExecutor as mirakuru already implements same functionality

0.5.2
-----

* syntax fixes for python 3
* moved postgresql starting code into it's own executor
* xdist distributed hosts testing bugfix (but xdist parallelization on one host won't work)

0.5.1
-----

* make rabbitmq logs persistent

0.5.0
-----

* update mirakuru to min 0.2
* os.killpg to terminate process
* add tests coverage on coveralls

0.4.22
------

* remove creating old RABBITMQ env variables

0.4.21
------

* remove elasticsearch home folder at process teardown
* set elasticsearch index.store.type to memory by default
* localized elasticsearch instance by default
* replaced summon_process with mirakuru

0.4.20
------

* RabbitMQ process fixture is session scoped
* rabbitmq fixture factory accepts custom teardown


0.4.19
------

* StopRunningExecutor to simply return if process had been already killed.

0.4.18
------

* MongoDB fixtures can be now initialized by factories


0.4.17
------

* Bugfix: params in redis fixture


0.4.16
-------

* Add params to mysql fixture


0.4.15
-------

* Client fixtures now check if process (process fixture) is running before
  every test and starts process if it was terminated after previous test.


0.4.14
-------

* Bugfix: Now we don't overwrite postgresql config in postgres_proc


0.4.13
-------

* Bugfix of rabbitmq_proc fixture - now it works with scope=function


0.4.12
-------

* Overrides SimpleExecutor's behavior with a try of more gentle terminating
  subprocess before killing it.
* Deprecate scope for mysqldb fixture and change it to function by default.
* RabbitMQ factories support (multiple rabbit fixtures).


0.4.10
-------

* Postgresql multiple versions proper support
* Default timeouts and waits for process executors


0.4.8
-------

* introduced Elasticsearch fixture


0.4.6
-------

* mysql fixture now uses factories


0.4.4
-------

* postgresql fixtures and fixture factories
* small code quality improvements
* pylama code check


0.4.3
-------

* splits rabbitmq fixture into process/client fixtures
