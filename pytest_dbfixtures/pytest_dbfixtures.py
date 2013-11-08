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
import subprocess
import shutil
from tempfile import mkdtemp

import pytest
from path import path
from pymlconf import ConfigManager
from summon_process.executors import TCPCoordinatedExecutor


ROOT_DIR = path(__file__).parent.parent.abspath()


def get_config(request):
    config_name = request.config.getvalue('db_conf')
    return ConfigManager(files=[config_name])


def try_import(module, request, pypi_package=None):
    try:
        i = importlib.import_module(module)
    except ImportError:
        raise ImportError(
            'Please install {0} package.\n'
            'pip install -U {0}'.format(
                pypi_package or module
            )
        )
    else:

        return i, get_config(request)


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


@pytest.fixture(scope='session')
def redis_proc(request):
    config = get_config(request)
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

    request.addfinalizer(redis_executor.stop)
    return redis_executor


@pytest.fixture
def redisdb(request, redis_proc):
    redis, config = try_import('redis', request)

    redis_client = redis.Redis(
        config.redis.host,
        config.redis.port,
        config.redis.db,
    )
    request.addfinalizer(redis_client.flushall)
    return redis_client


@pytest.fixture(scope='session')
def mongo_proc(request):
    config = get_config(request)
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

    def stop():
        mongo_executor.stop()
    request.addfinalizer(stop)
    return mongo_executor


@pytest.fixture
def mongodb(request, mongo_proc):
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
    return os.environ.get(name) or os.environ.get(name.split('RABBITMQ_')[1])


def get_rabbit_path(name):
    env = get_rabbit_env(name)
    if not env or not path(env).exists():
        return
    return path(env)


@pytest.fixture
def rabbitmq(request):
    pika, config = try_import('pika', request)

    rabbit_conf = open(request.config.getvalue('rabbit_conf')).readlines()
    rabbit_conf = dict(line[:-1].split('=') for line in rabbit_conf)

    tmpdir = path(mkdtemp(prefix='rabbitmq_fixture'))
    rabbit_conf['RABBITMQ_LOG_BASE'] = str(tmpdir)
    rabbit_conf['RABBITMQ_MNESIA_BASE'] = str(tmpdir)

    # setup environment variables
    for name, value in rabbit_conf.items():
        # for new versions of rabbitmq-server:
        os.environ[name] = value
        # for older versions of rabbitmq-server:
        prefix, name = name.split('RABBITMQ_')
        os.environ[name] = value

    rabbit_executor = TCPCoordinatedExecutor(
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

    rabbit_params = pika.connection.ConnectionParameters(
        host=config.rabbit.host,
        port=config.rabbit.port,
        connection_attempts=3,
        retry_delay=2,
    )
    pid_file = base_path / get_rabbit_env('RABBITMQ_NODENAME') + '.pid'
    wait_cmd = config.rabbit.rabbit_ctl, '-q', 'wait', pid_file
    subprocess.Popen(wait_cmd).communicate()
    try:
        rabbit_connection = pika.BlockingConnection(rabbit_params)
    except pika.adapters.blocking_connection.exceptions.ConnectionClosed:
        print "Be sure that you're connecting rabbitmq-server >= 2.8.4"
    return rabbit_connection


def remove_mysql_directory(config):
    if os.path.isdir(config.mysql.datadir):
        shutil.rmtree(config.mysql.datadir)


def init_mysql_directory(config):
    remove_mysql_directory(config)
    init_directory = (
        config.mysql.mysql_init,
        '--user=%s' % os.getenv('USER'),
        '--datadir=%s' % config.mysql.datadir,
    )
    subprocess.check_output(' '.join(init_directory), shell=True)


@pytest.fixture(scope='session')
def mysql_proc(request):
    config = get_config(request)
    init_mysql_directory(config)

    mysql_executor = TCPCoordinatedExecutor(
        '''
            {mysql_server} --datadir={datadir} --pid-file={pidfile}
            --port={port} --socket={socket} --log-error={logfile}
            --skip-syslog
        '''.format(
        mysql_server=config.mysql.mysql_server,
        datadir=config.mysql.datadir,
        pidfile=config.mysql.pidfile,
        port=config.mysql.port,
        socket=config.mysql.socket,
        logfile=config.mysql.logfile,
    ),
        host=config.mysql.host,
        port=config.mysql.port,
    )
    mysql_executor.start()

    def shutdown_server():
        return (
            config.mysql.mysql_admin,
            '--socket=%s' % config.mysql.socket,
            '--user=%s' % config.mysql.user,
            'shutdown'
        )

    def stop_server_and_remove_directory():
        subprocess.check_output(' '.join(shutdown_server()), shell=True)
        mysql_executor.stop()
        remove_mysql_directory(config)

    request.addfinalizer(stop_server_and_remove_directory)
    return mysql_executor


def mysqldb_fixture_factory(scope):
    @pytest.fixture(scope)
    def mysqldb_fixture(request, mysql_proc):
        config = get_config(request)

        MySQLdb, config = try_import(
            'MySQLdb', request, pypi_package='MySQL-python'
        )

        mysql_conn = MySQLdb.connect(
            host=config.mysql.host,
            unix_socket=config.mysql.socket,
            user=config.mysql.user,
            passwd=config.mysql.password,
        )

        mysql_conn.query('CREATE DATABASE %s' % config.mysql.db)
        mysql_conn.query('USE %s' % config.mysql.db)

        def drop_database():
            mysql_conn.query('DROP DATABASE IF EXISTS %s' % config.mysql.db)
            mysql_conn.close()

        request.addfinalizer(drop_database)
        return mysql_conn

mysqldb_session = mysqldb_fixture_factory(scope='session')
mysqldb = mysqldb_fixture_factory(scope='function')
