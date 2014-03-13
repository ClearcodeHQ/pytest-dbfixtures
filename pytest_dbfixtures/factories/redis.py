import pytest

from summon_process.executors import TCPCoordinatedExecutor

from pytest_dbfixtures.utils import get_config, try_import


def redis_proc(executable=None, params=None, config_file=None,
               host=None, port=None):
    """
    Redis process factory.

    :param str executable: path to redis-server
    :param str params: params
    :param str config_file: path to config file
    :param str host: hostname
    :param str port: port
    :rtype: func
    :returns: function which makes a redis process
    """

    @pytest.fixture(scope='session')
    def redis_proc_fixture(request):
        """
        #. Get configs.
        #. Run redis process.
        #. Stop redis process after tests.

        :param FixtureRequest request: fixture request object
        :rtype: summon_process.executors.tcp_coordinated_executor.TCPCoordinatedExecutor
        :returns: tcp executor
        """
        config = get_config(request)

        redis_exec = executable or config.redis.redis_exec
        redis_params = params or config.redis.params
        redis_conf = config_file or request.config.getvalue('redis_conf')
        redis_host = host or config.redis.host
        redis_port = port or config.redis.port

        pidfile = 'redis-server.{port}.pid'.format(port=redis_port)
        unixsocket = 'redis.{port}.sock'.format(port=redis_port)
        dbfilename = 'dump.{port}.rdb'.format(port=redis_port)
        logfile = 'redis-server.{port}.log'.format(port=redis_port)

        redis_executor = TCPCoordinatedExecutor(
            '''{redis_exec} {params} {config}
            --pidfile {pidfile} --unixsocket {unixsocket}
            --dbfilename {dbfilename} --logfile {logfile}
            --port {port}'''.format(redis_exec=redis_exec,
                                    params=redis_params,
                                    config=redis_conf,
                                    pidfile=pidfile,
                                    unixsocket=unixsocket,
                                    dbfilename=dbfilename,
                                    logfile=logfile,
                                    port=redis_port
                                    ),
            host=redis_host,
            port=redis_port,
        )
        redis_executor.start()

        request.addfinalizer(redis_executor.stop)

        return redis_executor

    return redis_proc_fixture


def redisdb(process_fixture_name, host=None, port=None, db=None):
    """
    Redis database factory.

    :param str process_fixture_name: name of the process fixture
    :param str host: hostname
    :param int port: port
    :param int db: number of database
    :rtype: func
    :returns: function which makes a connection to redis
    """

    @pytest.fixture
    def redisdb_factory(request):
        """
        #. Load required process fixture.
        #. Get redis module and config.
        #. Connect to redis.
        #. Flush database after tests.

        :param FixtureRequest request: fixture request object
        :rtype: redis.client.Redis
        :returns: Redis client
        """
        request.getfuncargvalue(process_fixture_name)

        redis, config = try_import('redis', request)

        redis_host = host or config.redis.host
        redis_port = port or config.redis.port
        redis_db = db or config.redis.db

        redis_client = redis.Redis(redis_host, redis_port, redis_db)
        request.addfinalizer(redis_client.flushall)

        return redis_client

    return redisdb_factory


__all__ = [redisdb, redis_proc]
