# Copyright (C) 2016 by Clearcode <http://clearcode.cc>
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

from pytest_dbfixtures.executors import TCPExecutor
from pytest_dbfixtures.port import get_port
from pytest_dbfixtures.utils import try_import, get_process_fixture


class JarPathException(Exception):
    """We do not know where user has dynamodb jar file.
    So, we want to tell him that he has to provide a path to dynamodb dir.

    We raise the exception when we won't find this file."""
    pass


def dynamodb_proc(dynamodb_dir=None, host='localhost', port=None, delay=False):
    """
    DynamoDB process factory.

    :param str dynamodb_dir: a path to dynamodb dir (without spaces)
    :param str host: hostname
    :param int port: port
    :param bool delay: causes DynamoDB to introduce delays for certain
        operations

    .. note::
        For more information visit:
            http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html

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
        path_dynamodb_jar = path(
            dynamodb_dir or request.config.getvalue('dynamodbdir')
        ) / 'DynamoDBLocal.jar'

        if not path_dynamodb_jar.exists():
            raise JarPathException(
                'You have to provide a path to the dir with dynamodb jar file.'
            )

        dynamodb_port = get_port(port)
        delay_arg = '-delayTransientStatuses' if delay else ''
        dynamodb_executor = TCPExecutor(
            '''java
            -Djava.library.path=./DynamoDBLocal_lib
            -jar {path_dynamodb_jar}
            -inMemory
            {delay}
            -port {port}'''
            .format(
                path_dynamodb_jar=path_dynamodb_jar,
                port=dynamodb_port,
                delay=delay_arg,
            ),
            host=host,
            port=dynamodb_port,
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
            https://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client
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

        # remove all tables
        request.addfinalizer(
            lambda: [t.delete() for t in dynamo_db.tables.all()]
        )

        return dynamo_db
    return dynamodb_factory

__all__ = [dynamodb_proc, dynamodb]
