'''
http://www.rabbitmq.com/configure.html
RabbitMQ is configured by environment variables and unfortunately they
have changed over time from 'bare' into the 'RABBITMQ_' prefixed ones.
Following code should consider both versions.
'''

import os
import subprocess
from tempfile import mkdtemp

import pytest
from path import path

from pytest_dbfixtures.utils import try_import, get_config
from pytest_dbfixtures.executors import TCPExecutor


def rabbit_env(name):
    """
    :param str name: name of environment variable
    :returns: value of rabbitmq's environment variable
    :rtype: str
    """
    return os.environ.get(name) or \
        os.environ.get(name.split('RABBITMQ_')[1])  # older versions of rabbit


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

    @pytest.fixture
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

        rabbit_confpath = config_file or request.config.getvalue('rabbit_conf')
        conf = open(rabbit_confpath).readlines()
        rabbit_conf = dict(line[:-1].split('=') for line in conf)

        tmpdir = path(mkdtemp(prefix='rabbitmq_pytest_fixture'))

        def rm():
            tmpdir.exists() and tmpdir.rmtree()
        request.addfinalizer(rm)

        log = (tmpdir / 'log').makedirs_p()
        mnesia = (tmpdir / 'mnesia').makedirs_p()
        rabbit_conf['RABBITMQ_LOG_BASE'] = str(log)
        rabbit_conf['RABBITMQ_MNESIA_BASE'] = str(mnesia)
        rabbit_conf['RABBITMQ_ENABLED_PLUGINS_FILE'] = str(tmpdir / 'plugins')

        for name, value in rabbit_conf.items():
            # for new versions of rabbitmq-server
            os.environ[name] = value
            # for older versions of rabbitmq-server
            prefix, name = name.split('RABBITMQ_')
            os.environ[name] = value

        config = get_config(request)

        rabbit_server = server or config.rabbit.rabbit_server
        rabbit_host = host or config.rabbit.host
        rabbit_port = port or config.rabbit.port

        os.environ['RABBITMQ_NODE_PORT'] = str(rabbit_port)
        os.environ['NODE_PORT'] = str(rabbit_port)

        rabbit_executor = TCPExecutor(
            rabbit_server,
            rabbit_host,
            rabbit_port,
        )

        request.addfinalizer(rabbit_executor.stop)

        base_path = rabbit_path('RABBITMQ_MNESIA_BASE')

        if node_name:
            os.environ['RABBITMQ_NODENAME'] = node_name

        rabbit_ctl = rabbit_ctl_file or config.rabbit.rabbit_ctl

        rabbit_executor.start()

        # In the end we want to use `rabbitctl wait` command to be certain
        # that our rabbitmq-server is really up and ready.
        pid_file = base_path / rabbit_env('RABBITMQ_NODENAME') + '.pid'
        wait_cmd = rabbit_ctl, '-q', 'wait', pid_file
        subprocess.Popen(wait_cmd).communicate()

        return rabbit_executor

    return rabbitmq_proc_fixture


def rabbitmq(process_fixture_name, host=None, port=None):
    '''
        Connects with RabbitMQ server

        :param str process_fixture_name: name of RabbitMQ preocess variable
                                         returned by rabbitmq_proc
        :param str host: RabbitMQ server host
        :param int port: RabbitMQ server port

        :returns RabbitMQ connection
    '''

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
        request.getfuncargvalue(process_fixture_name)

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

        return rabbit_connection

    return rabbitmq_factory
