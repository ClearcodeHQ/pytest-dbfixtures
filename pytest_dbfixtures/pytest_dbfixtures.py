import importlib

from path import path

from pymlconf import ConfigManager

from summon_process.executors import TCPCoordinatedExecutor


ROOT_DIR = path(__file__).parent.parent.abspath()


def try_import(module, request):
    try:
        i = importlib.import_module(module)
    except ImportError:
        raise ImportError("Please install {0} package.".format(module))
    else:
        config_name = request.config.getvalue('db_conf')
        config = ConfigManager(files=[config_name])

        return i, config


def pytest_addoption(parser):
    parser.addoption(
        '--dbfixtures-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'dbfixtures.conf',
        metavar='path',
        dest='db_conf',
    )

    parser.addoption(
        '--mongo-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'mongo.conf',
        metavar='path',
        dest='mongo_conf',
    )

    parser.addoption(
        '--redis-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'redis.conf',
        metavar='path',
        dest='redis_conf',
    )


def pytest_funcarg__redisdb(request):
    redis, config = try_import('redis', request)

    redis_conf = request.config.getvalue('redis_conf')

    redis_executor = TCPCoordinatedExecutor(
        '{redis_exec} {params} {config}'.format(
            redis_exec=config.redis.redis_exec,
            params=config.redis.params,
            config=redis_conf),
        host=config.redis.host,
        port=config.redis.port,
    )
    redis_executor.start()

    redis_client = redis.Redis(
        config.redis.host,
        config.redis.port,
        config.redis.db,
    )
    redis_client.flushall()

    def flush_and_stop():
        redis_client.flushall()
        redis_executor.stop()

    request.addfinalizer(flush_and_stop)
    return redis_client


def pytest_funcarg__mongodb(request):
    pymongo, config = try_import('pymongo', request)

    mongo_conf = request.config.getvalue('mongo_conf')

    mongo_executor = TCPCoordinatedExecutor(
        '{mongo_exec} {params} {config}'.format(
            mongo_exec=config.mongo.mongo_exec,
            params=config.mongo.params,
            config=mongo_conf),
        host=config.mongo.host,
        port=config.mongo.port,
    )
    mongo_executor.start()

    mongo_conn = pymongo.Connection(
        config.mongo.host,
        config.mongo.port
    )

    mongodb = mongo_conn[config.mongo.db]

    def drop_and_stop():
        for collection_name in mongodb.collection_names():
            if collection_name != 'system.indexes':
                mongodb[collection_name].drop()
        mongo_executor.stop()

    request.addfinalizer(drop_and_stop)
    return mongodb
