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
"""RabbitMQ client fixture factory."""

import pytest

from pytest_dbfixtures.utils import try_import


def clear_rabbitmq(process, rabbitmq_connection):
    """
    Clear queues and exchanges from given rabbitmq process.

    :param RabbitMqExecutor process: rabbitmq process
    :param rabbitpy.Connection rabbitmq_connection: connection to rabbitmq

    """
    from rabbitpy import Exchange, Queue
    channel = rabbitmq_connection.channel()
    process.set_environ()

    for exchange in process.list_exchanges():
        if exchange.startswith('amq.'):
            # ----------------------------------------------------------------
            # From rabbit docs:
            # https://www.rabbitmq.com/amqp-0-9-1-reference.html
            # ----------------------------------------------------------------
            # Exchange names starting with "amq." are reserved for pre-declared
            # and standardised exchanges. The client MAY declare an exchange
            # starting with "amq." if the passive option is set, or the
            # exchange already exists. Error code: access-refused
            # ----------------------------------------------------------------
            continue
        ex = Exchange(channel, exchange)
        ex.delete()

    for queue in process.list_queues():
        if queue.startswith('amq.'):
            # ----------------------------------------------------------------
            # From rabbit docs:
            # https://www.rabbitmq.com/amqp-0-9-1-reference.html
            # ----------------------------------------------------------------
            # Queue names starting with "amq." are reserved for pre-declared
            # and standardised queues. The client MAY declare a queue starting
            # with "amq." if the passive option is set, or the queue already
            # exists. Error code: access-refused
            # ----------------------------------------------------------------
            continue
        qu = Queue(channel, queue)
        qu.delete()


def rabbitmq(process_fixture_name, teardown=clear_rabbitmq):
    """
    Connects with RabbitMQ server

    :param str process_fixture_name: name of RabbitMQ process variable
        returned by rabbitmq_proc
    :param callable teardown: custom callable that clears rabbitmq

    .. note::

        calls to rabbitmqctl might be as slow or even slower
        as restarting process. To speed up, provide Your own teardown function,
        to remove queues and exchanges of your choosing, without querying
        rabbitmqctl underneath.

    :returns RabbitMQ connection
    """

    @pytest.fixture
    def rabbitmq_factory(request):
        """
        #. Get module and config.
        #. Connect to RabbitMQ using the parameters from config.

        :param TCPExecutor rabbitmq_proc: tcp executor
        :param FixtureRequest request: fixture request object
        :rtype: rabbitpy.adapters.blocking_connection.BlockingConnection
        :returns: instance of :class:`BlockingConnection`
        """

        # load required process fixture
        process = request.getfuncargvalue(process_fixture_name)

        rabbitpy, config = try_import('rabbitpy', request)

        connection = rabbitpy.Connection(
            'amqp://guest:guest@{host}:{port}/%2F'.format(
                host=process.host,
                port=process.port
            )
        )

        def finalizer():
            teardown(process, connection)
            connection.close()

        request.addfinalizer(finalizer)

        return connection

    return rabbitmq_factory
