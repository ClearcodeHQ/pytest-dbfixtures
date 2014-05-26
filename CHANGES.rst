CHANGES
=======


Current
-------

* MongoDB fixtures can be now initialized by factories


0.4.17
-------

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
