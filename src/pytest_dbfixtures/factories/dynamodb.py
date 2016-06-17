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

from pytest_dbfixtures.executors import TCPExecutor
from pytest_dbfixtures.utils import try_import, get_process_fixture


def dynamodb_proc(jar_path=None, host=None, port=None):
    """
    DynamoDB process factory.

    :param str jar_path: path to jar file (http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html?shortFooter=true)
    :param str host: hostname
    :param int port: port
    :return: function which makes a DynamoDB process
    """
    @pytest.fixture(scope='session')
    def dynamodb_proc_fixture(request):
        """
        #. Run a ``DynamoDBLocal.jar`` process.
        #. Stop ``DynamoDBLocal.jar`` process after tests.

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor
        """
        dynamodb_executor = TCPExecutor(
            '''java
            -Djava.library.path=./DynamoDBLocal_lib
            -jar {jar_path}
            -inMemory
            -port {port}'''
            .format(
                jar_path=jar_path,
                port=port
            ),
            host=host,
            port=port,
        )
        dynamodb_executor.start()
        request.addfinalizer(dynamodb_executor.stop)
        return dynamodb_executor
    return dynamodb_proc_fixture


def dynamodb(process_fixture_name):
    """
    DynamoDB resource factory.

    :param str process_fixture_name: name of the process fixture
    :rtype: func
    :returns: function which makes a connection to DynamoDB
    """

    @pytest.fixture
    def dynamodb_factory(request):
        """
        Connect to the local DynamoDB.

        :param FixtureRequest request: fixture request object
        :rtype: Subclass of :py:class:`~boto3.resources.base.ServiceResource`
        :returns: connection to DynamoDB database
        """
        proc_fixture = get_process_fixture(request, process_fixture_name)
        boto3, config = try_import('boto3', request)

        dynamo_db = boto3.resource(
            'dynamodb',
            endpoint_url='http://{host}:{port}'.format(
                host=proc_fixture.host,
                port=proc_fixture.port
            ),
            # these args do not matter (we have to put something to them)
            region_name='us-east-1',
            aws_access_key_id='',
            aws_secret_access_key='',
        )
        return dynamo_db
    return dynamodb_factory

__all__ = [dynamodb_proc, dynamodb]
