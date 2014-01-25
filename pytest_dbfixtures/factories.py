import pytest

from summon_process.executors import TCPCoordinatedExecutor

from pytest_dbfixtures.utils import get_config, try_import


def redis_proc(executable=None, params=None, config_file=None,
               host=None, port=None):

    @pytest.fixture(scope='session')
    def redis_proc_fixture(request):
        config = get_config(request)
        redis_exec = executable
        if not redis_exec:
            redis_exec = config.redis.redis_exec

        redis_params = params
        if not redis_params:
            redis_params = config.redis.params

        redis_conf = config_file
        if not redis_conf:
            redis_conf = request.config.getvalue('redis_conf')

        redis_host = host
        if not redis_host:
            redis_host = config.redis.host

        redis_port = port
        if not redis_port:
            redis_port = config.redis.port

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

    @pytest.fixture
    def redisdb_factory(request):
        # load required process fixture
        request.getfuncargvalue(process_fixture_name)

        redis, config = try_import('redis', request)

        redis_host = host
        if not redis_host:
            redis_host = config.redis.host

        redis_port = port
        if not redis_port:
            redis_port = config.redis.port

        redis_db = db
        if not redis_db:
            redis_db = config.redis.db

        redis_client = redis.Redis(redis_host, redis_port, redis_db)
        request.addfinalizer(redis_client.flushall)
        return redis_client

    return redisdb_factory
