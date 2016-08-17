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
from tempfile import gettempdir

import pytest
from path import path

from pytest_dbfixtures.executors import TCPExecutor
from pytest_dbfixtures.utils import get_config, try_import,\
    get_process_fixture, extract_version, compare_version
from pytest_dbfixtures.port import get_port

REQUIRED_VERSION = '2.6'
"""
Minimum required version of redis that is accepted by pytest-dbfixtures.
"""


def redis_proc(executable=None, params=None, config_file=None,
               host=None, port=-1, logs_prefix=''):
    """
    Redis process factory.

    :param str executable: path to redis-server
    :param str params: params
    :param str config_file: path to config file
    :param str host: hostname
    :param str|int|tuple|set|list port:
        exact port (e.g. '8000', 8000)
        randomly selected port (None) - any random available port
        [(2000,3000)] or (2000,3000) - random available port from a given range
        [{4002,4003}] or {4002,4003} - random of 4002 or 4003 ports
        [(2000,3000), {4002,4003}] -random of given orange and set
    :param str logs_prefix: prefix for log filename
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
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor
        """
        config = get_config(request)

        redis_exec = executable or config.redis.redis_exec
        redis_params = params or config.redis.params
        redis_conf = config_file or request.config.getvalue('redis_conf')
        redis_host = host or config.redis.host
        redis_port = get_port(port) or get_port(config.redis.port)

        pidfile = 'redis-server.{port}.pid'.format(port=redis_port)
        unixsocket = 'redis.{port}.sock'.format(port=redis_port)
        dbfilename = 'dump.{port}.rdb'.format(port=redis_port)
        logsdir = path(request.config.getvalue('logsdir'))
        logfile_path = logsdir / '{prefix}redis-server.{port}.log'.format(
            prefix=logs_prefix,
            port=redis_port
        )

        redis_executor = TCPExecutor(
            '''{redis_exec} {config}
            --pidfile {pidfile} --unixsocket {unixsocket}
            --dbfilename {dbfilename} --logfile {logfile_path}
            --port {port} --dir {tmpdir} {params}'''
            .format(
                redis_exec=redis_exec,
                params=redis_params,
                config=redis_conf,
                pidfile=pidfile,
                unixsocket=unixsocket,
                dbfilename=dbfilename,
                logfile_path=logfile_path,
                port=redis_port,
                tmpdir=gettempdir(),
            ),
            host=redis_host,
            port=redis_port,
        )
        redis_version = extract_version(
            os.popen('{0} --version'.format(redis_exec)).read()
        )
        cv_result = compare_version(redis_version, REQUIRED_VERSION)
        if redis_version and cv_result < 0:
            raise RedisUnsupported(
                'Your version of Redis is not supported. '
                'Consider updating to Redis {0} at least. '
                'The currently installed version of Redis: {1}.'
                .format(REQUIRED_VERSION, redis_version))
        redis_executor.start()
        request.addfinalizer(redis_executor.stop)

        return redis_executor

    return redis_proc_fixture


def redisdb(process_fixture_name, db=None, strict=True):
    """
    Redis database factory.

    :param str process_fixture_name: name of the process fixture
    :param int db: number of database
    :param bool strict: if true, uses StrictRedis client class
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
        proc_fixture = get_process_fixture(request, process_fixture_name)

        redis, config = try_import('redis', request)

        redis_host = proc_fixture.host
        redis_port = proc_fixture.port
        redis_db = db or config.redis.db
        redis_class = redis.StrictRedis if strict else redis.Redis

        redis_client = redis_class(
            redis_host, redis_port, redis_db, decode_responses=True)
        request.addfinalizer(redis_client.flushall)

        return redis_client

    return redisdb_factory


class RedisUnsupported(Exception):
    pass


__all__ = [redisdb, redis_proc]
