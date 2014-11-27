CHANGES
=======

0.8.0
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
