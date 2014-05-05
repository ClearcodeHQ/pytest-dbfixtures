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

import pytest

from path import path

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
mysqldb = factories.mysqldb('mysql_proc')
mysqldb_session = factories.mysqldb('mysql_proc', scope='session')

elasticsearch_proc = factories.elasticsearch_proc()
elasticsearch = factories.elasticsearch('elasticsearch_proc')

rabbitmq_proc = factories.rabbitmq_proc()
rabbitmq = factories.rabbitmq('rabbitmq_proc')


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
