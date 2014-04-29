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
import pytest
import subprocess

from path import path
from tempfile import mkdtemp

from pytest_dbfixtures import factories
from pytest_dbfixtures.executors import TCPExecutor
from pytest_dbfixtures.utils import get_config, try_import


ROOT_DIR = path(__file__).parent.parent.abspath()


def pytest_addoption(parser):
    parser.addoption(
        '--dbfixtures-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'conf' / 'dbfixtures.conf',
        metavar='path',
        dest='db_conf',
    )

    parser.addoption(
        '--mongo-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'conf' / 'mongo.conf',
        metavar='path',
        dest='mongo_conf',
    )

    parser.addoption(
        '--redis-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'conf' / 'redis.conf',
        metavar='path',
        dest='redis_conf',
    )

    parser.addoption(
        '--rabbit-config',
        action='store',
        default=ROOT_DIR / 'pytest_dbfixtures' / 'conf' / 'rabbit.conf',
        metavar='path',
        dest='rabbit_conf',
    )


redis_proc = factories.redis_proc()
redisdb = factories.redisdb('redis_proc')

postgresql_proc = factories.postgresql_proc()
postgresql = factories.postgresql('postgresql_proc')

mysql_proc = factories.mysql_proc()
mysqldb = factories.mysqldb('mysql_proc', scope='function')
mysqldb_session = factories.mysqldb('mysql_proc')

elasticsearch_proc = factories.elasticsearch_proc()
elasticsearch = factories.elasticsearch('elasticsearch_proc')


@pytest.fixture(scope='session')
def mongo_proc(request):
    """
    #. Get config.
    #. Run a ``mongod`` process.
    #. Stop ``mongod`` process after tests.

    .. note::
        `mongod <http://docs.mongodb.org/v2.2/reference/mongod/>`_

    :param FixtureRequest request: fixture request object
    :rtype: pytest_dbfixtures.executors.TCPExecutor
    :returns: tcp executor
    """
    config = get_config(request)
    mongo_conf = request.config.getvalue('mongo_conf')

    mongo_executor = TCPExecutor(
        '{mongo_exec} {params} {config}'.format(
            mongo_exec=config.mongo.mongo_exec,
            params=config.mongo.params,
            config=mongo_conf),
        host=config.mongo.host,
        port=config.mongo.port,
    )
    mongo_executor.start()

    def stop():
        mongo_executor.stop()

    request.addfinalizer(stop)

    return mongo_executor


@pytest.fixture
def mongodb(request, mongo_proc):
    """
    #. Get pymongo module and config.
    #. Get connection to mongo.
    #. Drop collections before and after tests.

    :param FixtureRequest request: fixture request object
    :param TCPExecutor mongo_proc: tcp executor
    :rtype: pymongo.connection.Connection
    :returns: connection to mongo database
    """
    pymongo, config = try_import('pymongo', request)

    mongo_conn = pymongo.Connection(
        config.mongo.host,
        config.mongo.port
    )

    def drop():
        for db in mongo_conn.database_names():
            for collection_name in mongo_conn[db].collection_names():
                if collection_name != 'system.indexes':
                    mongo_conn[db][collection_name].drop()

    request.addfinalizer(drop)

    drop()

    return mongo_conn


def get_rabbit_env(name):
    """
    Get value from environment variable. If does not exists (older version)
    then use older name.

    :param str name: name of environment variable
    :rtype: str
    :returns: path to directory
    """
    return os.environ.get(name) or os.environ.get(name.split('RABBITMQ_')[1])


def get_rabbit_path(name):
    """
    Get a path to directory contains sub-directories for the RabbitMQ
    server's Mnesia database files.
    `Relocate <http://www.rabbitmq.com/relocate.html>`_

    If environment variable or path to directory do not exist, return ``None``,
    else return path to directory.

    :param str name: name of environment variable
    :rtype: path.path or None
    :returns: path to directory
    """
    env = get_rabbit_env(name)

    if not env or not path(env).exists():
        return

    return path(env)


@pytest.fixture
def rabbitmq_proc(request):
    """
    #. Get config.
    #. Make a temporary directory.
    #. Setup environment variables.
    #. Start a rabbit server
        `<http://www.rabbitmq.com/man/rabbitmq-server.1.man.html>`_
    #. Stop rabbit server and remove temporary files after tests.

    :param FixtureRequest request: fixture request object
    :rtype: pytest_dbfixtures.executors.TCPExecutor
    :returns: tcp executor
    """

    rabbit_conf = open(request.config.getvalue('rabbit_conf')).readlines()
    rabbit_conf = dict(line[:-1].split('=') for line in rabbit_conf)

    tmpdir = path(mkdtemp(prefix='rabbitmq_fixture'))
    rabbit_conf['RABBITMQ_LOG_BASE'] = str(tmpdir)
    rabbit_conf['RABBITMQ_MNESIA_BASE'] = str(tmpdir)

    for name, value in rabbit_conf.items():
        # for new versions of rabbitmq-server
        os.environ[name] = value
        # for older versions of rabbitmq-server
        prefix, name = name.split('RABBITMQ_')
        os.environ[name] = value

    pika, config = try_import('pika', request)

    rabbit_executor = TCPExecutor(
        config.rabbit.rabbit_server,
        config.rabbit.host,
        config.rabbit.port,
    )
    base_path = get_rabbit_path('RABBITMQ_MNESIA_BASE')

    def stop_and_reset():
        rabbit_executor.stop()
        base_path.rmtree()
        tmpdir.exists() and tmpdir.rmtree()

    request.addfinalizer(stop_and_reset)

    rabbit_executor.start()
    pid_file = base_path / get_rabbit_env('RABBITMQ_NODENAME') + '.pid'
    wait_cmd = config.rabbit.rabbit_ctl, '-q', 'wait', pid_file
    subprocess.Popen(wait_cmd).communicate()

    return rabbit_executor


@pytest.fixture
def rabbitmq(rabbitmq_proc, request):
    """
    #. Get module and config.
    #. Connect to RabbitMQ using the parameters from config.

    :param TCPExecutor rabbitmq_proc: tcp executor
    :param FixtureRequest request: fixture request object
    :rtype: pika.adapters.blocking_connection.BlockingConnection
    :returns: instance of :class:`BlockingConnection`
    """
    pika, config = try_import('pika', request)

    rabbit_params = pika.connection.ConnectionParameters(
        host=config.rabbit.host,
        port=config.rabbit.port,
        connection_attempts=3,
        retry_delay=2,
    )

    try:
        rabbit_connection = pika.BlockingConnection(rabbit_params)
    except pika.adapters.blocking_connection.exceptions.ConnectionClosed:
        print "Be sure that you're connecting rabbitmq-server >= 2.8.4"

    return rabbit_connection
