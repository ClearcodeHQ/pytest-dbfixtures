CHANGES
=======

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
