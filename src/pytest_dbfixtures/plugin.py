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
import warnings


from path import path
import pytest

from pytest_dbfixtures import factories


ROOT_DIR = path(__file__).parent.parent.abspath()
CONF_DIR = ROOT_DIR / 'pytest_dbfixtures' / 'conf'


def pytest_addoption(parser):
    parser.addoption(
        '--dbfixtures-config',
        action='store',
        default=str(CONF_DIR / 'dbfixtures.conf'),
        metavar='path',
        dest='db_conf',
    )

    parser.addoption(
        '--redis-config',
        action='store',
        default=str(CONF_DIR / 'redis.conf'),
        metavar='path',
        dest='redis_conf',
    )

    parser.addoption(
        '--rabbit-config',
        action='store',
        default=str(CONF_DIR / 'rabbit.conf'),
        metavar='path',
        dest='rabbit_conf',
    )

    parser.addoption(
        '--dbfixtures-logsdir',
        action='store',
        default='/tmp',
        metavar='path',
        dest='logsdir',
    )

    parser.addoption(
        '--dynamodb-dir',
        action='store',
        default='/tmp/dynamodb',
        metavar='path',
        dest='dynamodbdir',
    )


def pytest_load_initial_conftests(early_config, parser, args):
    """Validate paths passed to py.test."""
    db_conf = early_config.getvalue('db_conf')
    if db_conf and not path(db_conf).isfile():
        raise ValueError(
            'argument passed to --dbfixtures-config is not a valid file path'
        )
    redis_conf = early_config.getvalue('redis_conf')
    if redis_conf and not path(redis_conf).isfile():
        raise ValueError(
            'argument passed to --redis-config is not a valid file path'
        )
    rabbit_conf = early_config.getvalue('rabbit_conf')
    if rabbit_conf and not path(rabbit_conf).isfile():
        raise ValueError(
            'argument passed to --rabbit-config is not a valid file path'
        )


redis_proc = factories.redis_proc()
redisdb = factories.redisdb('redis_proc')

mysql_proc = factories.mysql_proc()
mysql = factories.mysql('mysql_proc')


@pytest.fixture
def mysqldb(mysql):
    warnings.warn(
        '`mysqldb` fixture is deprecated. Please use `mysql` instead.',
        DeprecationWarning,
        2
    )
    return mysql

rabbitmq_proc = factories.rabbitmq_proc()
rabbitmq = factories.rabbitmq('rabbitmq_proc')

dynamodb_proc = factories.dynamodb_proc()
dynamodb = factories.dynamodb('dynamodb_proc')
