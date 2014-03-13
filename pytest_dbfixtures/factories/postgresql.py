import os
import pytest
import shutil
import subprocess
import time

from summon_process.executors import TCPCoordinatedExecutor

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from pytest_dbfixtures.utils import get_config, try_import


START_INFO = 'database system is ready to accept connections'


def wait_for_postgres(config, awaited_msg):
    """
    Blocks until logfile is created by psql server.
    Awaits for given message in logfile. Block until log contains message.

    :param pymlconf.ConfigManager config: config
    :param str awaited_msg: awaited message
    """
    while not os.path.isfile(config.postgresql.logfile):
        time.sleep(1)

    while 1:
        with open(config.postgresql.logfile, 'r') as content_file:
            content = content_file.read()
            if awaited_msg in content:
                break
        time.sleep(1)


def remove_postgresql_directory(config):
    """
    Checks postgresql directory and logfile. Delete a logfile if exist.
    Recursively delete a directory tree if exist.

    :param pymlconf.ConfigManager config: config
    """
    if os.path.isfile(config.postgresql.logfile):
        os.remove(config.postgresql.logfile)
    if os.path.isdir(config.postgresql.datadir):
        shutil.rmtree(config.postgresql.datadir)


def init_postgresql_directory(config):
    """
    #. Remove postgresql directory if exist.
    #. `Initialize postgresql data directory <www.postgresql.org/docs/9.1/static/app-initdb.html>`_

    :param pymlconf.ConfigManager config: config
    """
    remove_postgresql_directory(config)
    init_directory = (
        config.postgresql.postgresql_ctl, 'initdb',
        '-o "--auth=trust --username=%s"' % config.postgresql.user,
        '-D %s' % config.postgresql.datadir,
    )
    subprocess.check_output(' '.join(init_directory), shell=True)


def init_postgresql_database(postgresql, config):
    """
    #. Connect to psql with proper isolation level
    #. Create test database
    #. Close connection

    :param FixtureRequest postgresql: psycopg2 object
    :param pymlconf.ConfigManager config: config
    """
    conn = postgresql.connect(
        user=config.postgresql.user,
        host=config.postgresql.host,
        port=config.postgresql.port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE ' + config.postgresql.db)
    cur.close()
    conn.close()


def drop_postgresql_database(postgresql, config):
    """
    #. Connect to psql with proper isolation level
    #. Drop test database
    #. Close connection

    :param FixtureRequest postgresql: psycopg2 object
    :param pymlconf.ConfigManager config: config
    """
    conn = postgresql.connect(
        user=config.postgresql.user,
        host=config.postgresql.host,
        port=config.postgresql.port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('DROP DATABASE IF EXISTS %s' % config.postgresql.db)
    cur.close()
    conn.close()


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
        #. `Start a postgresqld server http://www.postgresql.org/docs/9.1/static/app-pg-ctl.html`_
        #. Stop server and remove directory after tests. `<http://www.postgresql.org/docs/9.1/static/app-pg-ctl.html>`_

        :param FixtureRequest request: fixture request object
        :rtype: summon_process.executors.tcp_coordinated_executor.TCPCoordinatedExecutor
        :returns: tcp executor
        """
        config = get_config(request)
        config.postgresql.host = host or config.postgresql.host
        config.postgresql.port = port or config.postgresql.port
        config.postgresql.datadir += str(config.postgresql.port)
        config.postgresql.logfile += str(config.postgresql.port)

        init_postgresql_directory(config)

        postgresql_executor = TCPCoordinatedExecutor(
            '''
                {postgresql_ctl} start -D {datadir}
                -o "-F -p {port} -c unix_socket_directory='{unixsocketdir}'"
                -l {logfile} {startparams}
            '''.format(
            postgresql_ctl=config.postgresql.postgresql_ctl,
            datadir=config.postgresql.datadir,
            port=config.postgresql.port,
            unixsocketdir=config.postgresql.unixsocketdir,
            logfile=config.postgresql.logfile,
            startparams=config.postgresql.startparams,
        ),
            host=config.postgresql.host,
            port=config.postgresql.port,
        )
        postgresql_executor.start()
        if '-w' in config.postgresql.startparams:
            wait_for_postgres(config, START_INFO)

        def shutdown_server():
            return (
                config.postgresql.postgresql_ctl, 'stop',
                '-D %s' % config.postgresql.datadir,
                '-o "-p %s -c unix_socket_directory=\'%s\'"' % (
                    config.postgresql.port, config.postgresql.unixsocketdir)
            )

        def stop_server_and_remove_directory():
            subprocess.check_output(' '.join(shutdown_server()), shell=True)
            postgresql_executor.stop()
            remove_postgresql_directory(config)

        request.addfinalizer(stop_server_and_remove_directory)

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

        postgresql, config = try_import('psycopg2', request)
        config.postgresql.host = host or config.postgresql.unixsocketdir
        config.postgresql.port = port or config.postgresql.port
        config.postgresql.db = db or config.postgresql.db

        init_postgresql_database(postgresql, config)
        conn = postgresql.connect(
            dbname=config.postgresql.db,
            user=config.postgresql.user,
            host=config.postgresql.host,
            port=config.postgresql.port
        )

        def drop_database():
            conn.close()
            drop_postgresql_database(postgresql, config)

        request.addfinalizer(drop_database)

        return conn

    return postgresql_factory


__all__ = [postgresql, postgresql_proc]
