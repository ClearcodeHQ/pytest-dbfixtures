import pytest
from summon_process.executors import TCPCoordinatedExecutor

from pytest_dbfixtures.utils import get_config


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

        redis_executor = TCPCoordinatedExecutor(
            '{redis_exec} {params} {config} --pidfile {pidfile}'.format(
                redis_exec=redis_exec,
                params=redis_params,
                config=redis_conf,
                pidfile=pidfile),
            host=redis_host,
            port=redis_port,
        )
        redis_executor.start()

        request.addfinalizer(redis_executor.stop)
        return redis_executor

    return redis_proc_fixture
