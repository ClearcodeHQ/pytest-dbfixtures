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


from path import path

from pytest_dbfixtures import factories


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

mongo_proc = factories.mongo_proc()
mongodb = factories.mongodb('mongo_proc')
