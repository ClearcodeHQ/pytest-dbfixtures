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
import shutil
import subprocess

import pytest

from pytest_dbfixtures.executors import TCPExecutor
from pytest_dbfixtures.utils import get_config


def remove_mysql_directory(datadir):
    """
    Check mysql directory. Recursively delete a directory tree if exist.

    :param str datadir: path to datadir

    """
    if os.path.isdir(datadir):
        shutil.rmtree(datadir)


def init_mysql_directory(mysql_init, datadir):
    """
    #. Remove mysql directory if exist.
    #. `Initialize MySQL data directory
        <https://dev.mysql.com/doc/refman/5.0/en/mysql-install-db.html>`_

    :param str mysql_init: mysql_init executable
    :param str datadir: path to datadir

    """
    remove_mysql_directory(datadir)
    init_directory = (
        mysql_init,
        '--user=%s' % os.getenv('USER'),
        '--datadir=%s' % datadir,
    )
    subprocess.check_output(' '.join(init_directory), shell=True)


def mysql_proc(executable=None, admin_executable=None, init_executable=None,
               host=None, port=None, params=None):
    """
    Mysql server process factory.

    :param str executable: path to mysql executable
    :param str admin_executable: path to mysql_admin executable
    :param str init_executable: path to mysql_init executable
    :param str host: hostname
    :param str port: port

    :rtype: func
    :returns: function which makes a redis process

    """

    @pytest.fixture(scope='session')
    def mysql_proc_fixture(request):
        """
        #. Get config.
        #. Initialize MySQL data directory
        #. `Start a mysqld server
            <https://dev.mysql.com/doc/refman/5.0/en/mysqld-safe.html>`_
        #. Stop server and remove directory after tests.
            `See <https://dev.mysql.com/doc/refman/5.6/en/mysqladmin.html>`_

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor

        """
        config = get_config(request)
        mysql_exec = executable or config.mysql.mysql_server
        mysql_admin_exec = admin_executable or config.mysql.mysql_admin
        mysql_init = init_executable or config.mysql.mysql_init
        mysql_port = port or config.mysql.port
        mysql_host = host or config.mysql.host
        mysql_params = params or config.mysql.params

        datadir = '/tmp/mysqldata_{port}'.format(port=mysql_port)
        pidfile = '/tmp/mysql-server.{port}.pid'.format(port=mysql_port)
        unixsocket = '/tmp/mysql.{port}.sock'.format(port=mysql_port)
        logfile = '/tmp/mysql-server.{port}.log'.format(port=mysql_port)

        init_mysql_directory(mysql_init, datadir)

        mysql_executor = TCPExecutor(
            '''
            {mysql_server} --datadir={datadir} --pid-file={pidfile}
            --port={port} --socket={socket} --log-error={logfile}
            --skip-syslog {params}
            '''
            .format(
                mysql_server=mysql_exec,
                port=mysql_port,
                datadir=datadir,
                pidfile=pidfile,
                socket=unixsocket,
                logfile=logfile,
                params=mysql_params,
            ),
            host=mysql_host,
            port=mysql_port,
        )
        mysql_executor.start()

        def stop_server_and_remove_directory():
            shutdown_server = (
                mysql_admin_exec,
                '--socket=%s' % unixsocket,
                '--user=%s' % config.mysql.user,
                'shutdown'
            )
            subprocess.check_output(' '.join(shutdown_server), shell=True)
            mysql_executor.stop()
            remove_mysql_directory(datadir)

        request.addfinalizer(stop_server_and_remove_directory)

        return mysql_executor

    return mysql_proc_fixture
