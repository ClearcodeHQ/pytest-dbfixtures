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
import pytest

from pytest_dbfixtures.utils import get_config, try_import, get_process_fixture


def mysqldb(process_fixture_name, scope=None,
            user=None, passwd=None, db=None,
            host=None, port=None,
            charset='utf8', collation='utf8_general_ci'):
    """
    Factory. Create connection to mysql. If you want you can give a scope,
    default is 'session'.

    For charset and collation meaning,
    see `Database Character Set and Collation
    <https://dev.mysql.com/doc/refman/5.5/en/charset-database.html>`_

    .. warning::

        scope argument is deprecated!

    :param str process_fixture_name: process fixture name
    :param str scope: scope (session, function, module, etc.)
    :param str host: hostname
    :param str user: mysql server user
    :param str passwd: mysql server's password
    :param str db: database's name
    :param str port: port
    :param str charset: MySQL characterset to use by default
        for *tests* database
    :param str collation: MySQL collation to use by default
        for *tests* database

    :returns: function ``mysqldb_fixture`` with suit scope
    :rtype: func
    """
    if scope:
        # deprecate scope
        warnings.warn(
            '`scope` argument is deprecated. '
            'This fixture also automatically clears database after test '
            'So it\'s much better idea to have it simply function-scoped',
            DeprecationWarning,
            2
        )
    else:
        scope = 'function'

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
        get_process_fixture(request, process_fixture_name)

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

        mysql_conn.query(
            '''CREATE DATABASE {name}
            DEFAULT CHARACTER SET {charset}
            DEFAULT COLLATE {collation}'''
            .format(
                name=mysql_db, charset=charset, collation=collation
            )
        )
        mysql_conn.query('USE %s' % mysql_db)

        def drop_database():
            mysql_conn.query('DROP DATABASE IF EXISTS %s' % mysql_db)
            mysql_conn.close()

        request.addfinalizer(drop_database)

        return mysql_conn

    return mysqldb_fixture
