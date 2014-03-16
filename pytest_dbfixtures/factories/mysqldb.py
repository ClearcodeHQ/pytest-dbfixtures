import pytest

from pytest_dbfixtures.utils import get_config, try_import


def mysqldb(process_fixture_name, scope='session',
            user=None, passwd=None, db=None,
            host=None, port=None):
    """
    Factory. Create connection to mysql. If you want you can give a scope,
    default is 'session'.

    :param str process_fixture_name: process fixture name
    :param str scope: scope (session, function, module, etc.)
    :param str host: hostname
    :param str user: mysql server user
    :param str passwd: mysql server's password
    :param str db: database's name
    :param str port: port
    :rtype: func
    :returns: function ``mysqldb_fixture`` with suit scope
    """

    @pytest.fixture(scope)
    def mysqldb_fixture(request):
        """
        #. Get config.
        #. Try to import MySQLdb package.
        #. Connect to mysql server.
        #. Create database.
        #. Use proper database.
        #. Drop database after tests.

        :param FixtureRequest request: fixture request object

        :rtype: MySQLdb.connections.Connection
        :returns: connection to database
        """
        request.getfuncargvalue(process_fixture_name)

        config = get_config(request)
        mysql_port = port or config.mysql.port
        mysql_host = host or config.mysql.host
        mysql_user = user or config.mysql.user
        mysql_passwd = passwd or config.mysql.password
        mysql_db = db or config.mysql.db

        unixsocket = '/tmp/mysql.{port}.sock'.format(port=mysql_port)

        MySQLdb, config = try_import(
            'MySQLdb', request, pypi_package='MySQL-python'
        )

        mysql_conn = MySQLdb.connect(
            host=mysql_host,
            unix_socket=unixsocket,
            user=mysql_user,
            passwd=mysql_passwd,
        )

        mysql_conn.query('CREATE DATABASE %s' % mysql_db)
        mysql_conn.query('USE %s' % mysql_db)

        def drop_database():
            mysql_conn.query('DROP DATABASE IF EXISTS %s' % mysql_db)
            mysql_conn.close()

        request.addfinalizer(drop_database)

        return mysql_conn

    return mysqldb_fixture
