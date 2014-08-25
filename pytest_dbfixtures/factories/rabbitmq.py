import os
import subprocess

import pytest
from path import path

from pytest_dbfixtures.utils import try_import, get_config
from pytest_dbfixtures.executors import TCPExecutor


class RabbitMqExecutor(TCPExecutor):

    """
    RabbitMQ executor to start specific rabbitmq instances.
    """

    def __init__(self, command, host, port, rabbit_ctl, environ, **kwargs):
        """
        Initialize RabbitMQ executor.

        :param str command: rabbitmq-server location
        :param str host: host where rabbitmq will be accessible
        :param int port: port under which rabbitmq runs
        :param str rabbit_ctl: rabbitctl location
        :param dict environ: rabbitmq configuration environment variables
        :param kwargs: see TCPExecutor for description
        """
        super(RabbitMqExecutor, self).__init__(command, host, port, **kwargs)
        self.rabbit_ctl = rabbit_ctl
        self.env = environ

    def set_environ(self):
        for env, value in self.env.iteritems():
            os.environ[env] = value

    def start(self):
        self.set_environ()
        TCPExecutor.start(self)

    def rabbitctl_output(self, *args):
        """
        Queries rabbitctl with args

        :param list args: list of additional args to query
        """
        self.set_environ()
        ctl_command = [self.rabbit_ctl]
        ctl_command.extend(args)
        return subprocess.check_output(ctl_command)

    def list_exchanges(self):
        """Get exchanges defined on given rabbitmq."""
        exchanges = []
        output = self.rabbitctl_output('list_exchanges', 'name')
        unwanted_exchanges = ['Listing exchanges ...', '...done.']

        for exchange in output.split('\n'):
            if exchange and exchange not in unwanted_exchanges:
                exchanges.append(exchange)

        return exchanges

    def list_queues(self):
        """Get queues defined on given rabbitmq."""
        queues = []
        output = self.rabbitctl_output('list_queues', 'name')
        unwanted_queues = ['Listing queues ...', '...done.']

        for queue in output.split('\n'):
            if queue and queue not in unwanted_queues:
                queues.append(queue)

        return queues


def rabbit_env(name):
    """
    :param str name: name of environment variable
    :returns: value of rabbitmq's environment variable
    :rtype: str
    """
    return os.environ.get(name)


def rabbit_path(name):
    """
    Get a path to directory containing sub-directories for the RabbitMQ
    server's Mnesia database files.
    `Relocate <http://www.rabbitmq.com/relocate.html>`_

    If environment variable or path to directory do not exist, return ``None``,
    else return path to directory.

    :param str name: name of environment variable
    :rtype: path.path or None
    :returns: path to directory
    """
    env = rabbit_env(name)

    if not env:
        return

    env = path(env)

    if not env.exists():
        return

    return path(env)


def rabbitmq_proc(config_file=None, server=None, host=None, port=None,
                  node_name=None, rabbit_ctl_file=None):
    '''
        Starts RabbitMQ as a subprocess.

        :param str config_file: path to config file
        :param str server: path to rabbitmq-server command
        :param str host: server host
        :param int port: server port
        :param str node_name: RabbitMQ node name used for setting environment
                              variable RABBITMQ_NODENAME
        :param str rabbit_ctl_file: path to rabbitmqctl file

        :returns pytest fixture with RabbitMQ process executor
    '''

    @pytest.fixture(scope='session')
    def rabbitmq_proc_fixture(request):
        """
        #. Get config.
        #. Make a temporary directory.
        #. Setup required environment variables:
        #.  * RABBITMQ_LOG_BASE
        #.  * RABBITMQ_MNESIA_BASE
        #.  * RABBITMQ_ENABLED_PLUGINS_FILE
        #.  * RABBITMQ_NODE_PORT
        #.  * RABBITMQ_NODENAME
        #. Start a rabbit server
            `<http://www.rabbitmq.com/man/rabbitmq-server.1.man.html>`_
        #. Stop rabbit server and remove temporary files after tests.

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor of running rabbitmq-server
        """

        config = get_config(request)
        rabbit_confpath = config_file or request.config.getvalue('rabbit_conf')

        with open(rabbit_confpath) as configuration:
            environ = dict(
                line[:-1].split('=') for line in configuration.readlines()
            )

        rabbit_ctl = rabbit_ctl_file or config.rabbit.rabbit_ctl
        rabbit_server = server or config.rabbit.rabbit_server
        rabbit_host = host or config.rabbit.host
        rabbit_port = port or config.rabbit.port

        rabbit_path = path('/tmp/rabbitmq.{0}/'.format(rabbit_port))
        rabbit_log = rabbit_path + 'log'
        rabbit_mnesia = rabbit_path + 'mnesia'
        rabbit_plugins = rabbit_path + 'plugins'

        environ['RABBITMQ_LOG_BASE'] = rabbit_log
        environ['RABBITMQ_MNESIA_BASE'] = rabbit_mnesia
        environ['RABBITMQ_ENABLED_PLUGINS_FILE'] = rabbit_plugins
        environ['RABBITMQ_NODE_PORT'] = str(rabbit_port)

        if node_name:
            environ['RABBITMQ_NODENAME'] = node_name

        rabbit_executor = RabbitMqExecutor(
            rabbit_server,
            rabbit_host,
            rabbit_port,
            rabbit_ctl,
            environ
        )

        request.addfinalizer(rabbit_executor.stop)

        rabbit_executor.start()

        return rabbit_executor

    return rabbitmq_proc_fixture


def clear_rabbitmq(process, pika_connection):
    """
    Clear queues and exchanges from given rabbitmq process.

    :param RabbitMqExecutor process: rabbitmq process
    :param pika.BlockingConnection pika_connection: connection to rabbitmq

    """
    channel = pika_connection.channel()
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
        channel.exchange_delete(exchange)

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
        channel.queue_delete(queue)


def rabbitmq(
        process_fixture_name, host=None, port=None, teardown=clear_rabbitmq):
    """
    Connects with RabbitMQ server

    :param str process_fixture_name: name of RabbitMQ process variable
        returned by rabbitmq_proc
    :param str host: RabbitMQ server host
    :param int port: RabbitMQ server port
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
        :rtype: pika.adapters.blocking_connection.BlockingConnection
        :returns: instance of :class:`BlockingConnection`
        """

        # load required process fixture
        process = request.getfuncargvalue(process_fixture_name)

        pika, config = try_import('pika', request)

        rabbit_params = pika.connection.ConnectionParameters(
            host=host or config.rabbit.host,
            port=port or config.rabbit.port,
            connection_attempts=3,
            retry_delay=2,
        )

        try:
            rabbit_connection = pika.BlockingConnection(rabbit_params)
        except pika.adapters.blocking_connection.exceptions.ConnectionClosed:
            print "Be sure that you're connecting rabbitmq-server >= 2.8.4"

        def finalizer():
            teardown(process, rabbit_connection)

        request.addfinalizer(finalizer)

        return rabbit_connection

    return rabbitmq_factory
