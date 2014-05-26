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
from tempfile import mkdtemp

from pytest_dbfixtures.executors import TCPExecutor
from pytest_dbfixtures.utils import get_config, try_import, get_process_fixture


def mongo_proc(executable=None, params=None, host=None, port=None):
    """
    Mongo process factory.

    :param str executable: path to mongod
    :param str params: params
    :param str host: hostname
    :param str port: port
    :rtype: func
    :returns: function which makes a mongo process
    """

    @pytest.fixture(scope='session')
    def mongo_proc_fixture(request):
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

        # make a temporary directory for tests and delete it
        # if tests have been finished
        tmpdir = path(mkdtemp(prefix='mongo_pytest_fixture'))
        request.addfinalizer(lambda: tmpdir.exists() and tmpdir.rmtree())

        mongo_exec = executable or config.mongo.mongo_exec
        mongo_params = params or config.mongo.params

        mongo_host = host or config.mongo.host
        mongo_port = port or config.mongo.port

        mongo_logpath = '/tmp/mongo.{port}.log'.format(port=mongo_port)

        mongo_executor = TCPExecutor(
            '{mongo_exec} --bind_ip {host} --port {port} --dbpath {dbpath} --logpath {logpath} {params}'.format(  # noqa
                mongo_exec=mongo_exec,
                params=mongo_params,
                host=mongo_host,
                port=mongo_port,
                dbpath=tmpdir,
                logpath=mongo_logpath,
            ),
            host=mongo_host,
            port=mongo_port,
        )
        mongo_executor.start()

        request.addfinalizer(mongo_executor.stop)

        return mongo_executor

    return mongo_proc_fixture


def mongodb(process_fixture_name, host=None, port=None):
    """
    Mongo database factory.

    :param str process_fixture_name: name of the process fixture
    :param str host: hostname
    :param int port: port
    :param int db: number of database
    :rtype: func
    :returns: function which makes a connection to mongo
    """

    @pytest.fixture
    def mongodb_factory(request):
        """
        #. Get pymongo module and config.
        #. Get connection to mongo.
        #. Drop collections before and after tests.

        :param FixtureRequest request: fixture request object
        :rtype: pymongo.connection.Connection
        :returns: connection to mongo database
        """
        get_process_fixture(request, process_fixture_name)

        pymongo, config = try_import('pymongo', request)

        mongo_host = host or config.mongo.host
        mongo_port = port or config.mongo.port

        mongo_conn = pymongo.Connection(
            mongo_host,
            mongo_port,
        )

        def drop():
            for db in mongo_conn.database_names():
                for collection_name in mongo_conn[db].collection_names():
                    if collection_name != 'system.indexes':
                        mongo_conn[db][collection_name].drop()

        drop()

        request.addfinalizer(drop)

        return mongo_conn

    return mongodb_factory


__all__ = [mongodb, mongo_proc]
