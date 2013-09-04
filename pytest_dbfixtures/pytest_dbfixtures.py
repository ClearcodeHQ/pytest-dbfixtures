# Copyright (C) 2013 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-dbfixtures.

# pytest-dbfixtures is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-dbfixtures is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-dbfixtures.  If not, see <http://www.gnu.org/licenses/>.

import os
import importlib
from subprocess import Popen

from path import path
from pymlconf import ConfigManager
from summon_process.executors import TCPCoordinatedExecutor


ROOT_DIR = path(__file__).parent.parent.abspath()


def try_import(module, request):
    try:
        i = importlib.import_module(module)
    except ImportError:
        raise ImportError('Please install {0} package.\n'
                          'pip install -U {0}'.format(module))
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

    parser.addoption(
        '--rabbit-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'rabbit.conf',
        metavar='path',
        dest='rabbit_conf',
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


def pytest_funcarg__rabbitmq(request):
    pika, config = try_import('pika', request)

    rabbit_conf = request.config.getvalue('rabbit_conf')
    for line in open(rabbit_conf):
        name, value = line[:-1].split('=')
        os.environ[name] = value

    rabbit_executor = TCPCoordinatedExecutor(
        '{rabbit_exec}'.format(
            rabbit_exec=config.rabbit.rabbit_server,
        ),
        host=config.rabbit.host,
        port=config.rabbit.port,
    )
    rabbit_executor.start()

    rabbit_params = pika.connection.ConnectionParameters(
        host=config.rabbit.host,
        port=config.rabbit.port,
    )
    rabbit_connection = pika.BlockingConnection(rabbit_params)

    def stop_and_cleanup():
        rabbit_executor.stop()
        Popen([config.rabbit.rabbit_ctl, 'force_reset'])
    request.addfinalizer(stop_and_cleanup)
    return rabbit_connection
