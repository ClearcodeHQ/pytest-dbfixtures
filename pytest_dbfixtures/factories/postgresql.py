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
import re
import shutil
import subprocess
import time

import pytest

from pytest_dbfixtures.executors import TCPExecutor
from pytest_dbfixtures.utils import get_config, try_import


START_INFO = 'database system is ready to accept connections'

BASE_PROC_START_COMMAND = """
{postgresql_ctl} start -D {datadir}
-o "-F -p {port} -c %s='{unixsocketdir}'"
-l {logfile} {startparams}"""

PROC_START_COMMAND = {
    '8.4': BASE_PROC_START_COMMAND % 'unix_socket_directory',
    '9.0': BASE_PROC_START_COMMAND % 'unix_socket_directory',
    '9.1': BASE_PROC_START_COMMAND % 'unix_socket_directory',
    '9.2': BASE_PROC_START_COMMAND % 'unix_socket_directory',
    '9.3': BASE_PROC_START_COMMAND % 'unix_socket_directories',
}


def wait_for_postgres(logfile, awaited_msg):
    """
    Blocks until logfile is created by psql server.
    Awaits for given message in logfile. Block until log contains message.

    :param str logfile: logfile path
    :param str awaited_msg: awaited message
    """
    while not os.path.isfile(logfile):
        time.sleep(1)

    while 1:
        with open(logfile, 'r') as content_file:
            content = content_file.read()
            if awaited_msg in content:
                break
        time.sleep(1)


def remove_postgresql_directory(logfile, datadir):
    """
    Checks postgresql directory and logfile. Delete a logfile if exist.
    Recursively delete a directory tree if exist.

    :param str logfile: logfile path
    :param str datadir: datadir path
    """
    if os.path.isfile(logfile):
        os.remove(logfile)
    if os.path.isdir(datadir):
        shutil.rmtree(datadir)


def init_postgresql_directory(postgresql_ctl, user, datadir, logfile):
    """
    #. Remove postgresql directory if exist.
    #. `Initialize postgresql data directory
        <www.postgresql.org/docs/9.3/static/app-initdb.html>`_

    :param str postgresql_ctl: ctl path
    :param str user: postgresql username
    :param str datadir: datadir path
    :param str logfile: logfile path

    """
    remove_postgresql_directory(logfile, datadir)
    init_directory = (
        postgresql_ctl, 'initdb',
        '-o "--auth=trust --username=%s"' % user,
        '-D %s' % datadir,
    )
    subprocess.check_output(' '.join(init_directory), shell=True)


def init_postgresql_database(psycopg2, user, host, port, db):
    """
    #. Connect to psql with proper isolation level
    #. Create test database
    #. Close connection

    :param module psycopg2: psycopg2 object
    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db: database name

    """

    conn = psycopg2.connect(user=user, host=host, port=port)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE ' + db)
    cur.close()
    conn.close()


def drop_postgresql_database(psycopg2, user, host, port, db):
    """
    #. Connect to psql with proper isolation level
    #. Drop test database
    #. Close connection

    :param module psycopg2: psycopg2 object
    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db: database name
    """
    conn = psycopg2.connect(user=user, host=host, port=port)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('DROP DATABASE IF EXISTS %s' % db)
    cur.close()
    conn.close()


def postgresql_version(postgresql_ctl):
    """
    Detect postgresql version.

    :return: minor version string
    :rtype: str
    """
    version_string = subprocess.check_output([postgresql_ctl, '--version'])
    matches = re.search('.* (?P<version>\d\.\d)\.\d', version_string)
    return matches.groupdict()['version']


def postgresql_proc(executable=None, host=None, port=None):
    """
    postgresql process factory.

    :param str executable: path to postgresql_ctl
    :param str host: hostname
    :param str port: port
    :rtype: func
    :returns: function which makes a postgresql process
    """

    @pytest.fixture(scope='session')
    def postgresql_proc_fixture(request):
        """
        #. Get config.
        #. Initialize postgresql data directory
        #. `Start a postgresqld server
            <http://www.postgresql.org/docs/9.1/static/app-pg-ctl.html>`_
        #. Stop server and remove directory after tests.
            `See <http://www.postgresql.org/docs/9.1/static/app-pg-ctl.html>`_

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor
        """
        config = get_config(request)
        postgresql_ctl = executable or config.postgresql.postgresql_ctl
        # check if that executable exists, as it's no on system PATH
        # only replace if executable isn't passed manually
        if not os.path.exists(postgresql_ctl) and executable is None:
            pg_bindir = subprocess.check_output(
                ['pg_config', '--bindir'], universal_newlines=True
            ).strip()
            postgresql_ctl = os.path.join(pg_bindir, 'pg_ctl')

        pg_host = host or config.postgresql.host
        pg_port = port or config.postgresql.port
        datadir = '/tmp/postgresqldata.{0}'.format(pg_port)
        logfile = '/tmp/postgresql.{0}.log'.format(pg_port)

        init_postgresql_directory(
            postgresql_ctl, config.postgresql.user, datadir, logfile
        )
        pg_version = postgresql_version(postgresql_ctl)
        postgresql_executor = TCPExecutor(
            PROC_START_COMMAND[pg_version].format(
                postgresql_ctl=postgresql_ctl,
                datadir=datadir,
                port=pg_port,
                unixsocketdir=config.postgresql.unixsocketdir,
                logfile=logfile,
                startparams=config.postgresql.startparams,
            ),
            host=pg_host,
            port=pg_port,
        )

        def stop_server_and_remove_directory():
            subprocess.check_output(
                '{postgresql_ctl} stop -D {datadir} '
                '-o "-p {port} -c unix_socket_directory=\'{unixsocketdir}\'"'
                .format(
                    postgresql_ctl=postgresql_ctl,
                    datadir=datadir,
                    port=pg_port,
                    unixsocketdir=config.postgresql.unixsocketdir
                ),
                shell=True)
            postgresql_executor.stop()
            remove_postgresql_directory(logfile, datadir)

        request.addfinalizer(stop_server_and_remove_directory)

        # start server
        postgresql_executor.start()
        if '-w' in config.postgresql.startparams:
            wait_for_postgres(logfile, START_INFO)

        return postgresql_executor

    return postgresql_proc_fixture


def postgresql(process_fixture_name, host=None, port=None, db=None):
    """
    postgresql database factory.

    :param str process_fixture_name: name of the process fixture
    :param str host: hostname
    :param int port: port
    :param int db: database name
    :rtype: func
    :returns: function which makes a connection to postgresql
    """

    @pytest.fixture
    def postgresql_factory(request):
        """
        #. Load required process fixture.
        #. Get postgresql module and config.
        #. Connect to postgresql.
        #. Flush database after tests.

        :param FixtureRequest request: fixture request object
        :rtype: psycopg2.connection
        :returns: postgresql client
        """
        request.getfuncargvalue(process_fixture_name)

        psycopg2, config = try_import('psycopg2', request)
        pg_host = host or config.postgresql.unixsocketdir
        pg_port = port or config.postgresql.port
        pg_db = db or config.postgresql.db

        init_postgresql_database(
            psycopg2, config.postgresql.user, pg_host, pg_port, pg_db
        )
        conn = psycopg2.connect(
            dbname=pg_db,
            user=config.postgresql.user,
            host=pg_host,
            port=pg_port
        )

        def drop_database():
            conn.close()
            drop_postgresql_database(
                psycopg2, config.postgresql.user, pg_host, pg_port, pg_db
            )

        request.addfinalizer(drop_database)

        return conn

    return postgresql_factory


__all__ = [postgresql, postgresql_proc]
