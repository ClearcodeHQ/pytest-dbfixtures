from pytest_dbfixtures import factories
from pytest_dbfixtures.factories.rabbitmq_client import clear_rabbitmq


def test_rabbitmq(rabbitmq):
    channel = rabbitmq.channel()
    assert channel.state == channel.OPEN


rabbitmq_proc2 = factories.rabbitmq_proc(port=5674, node_name='test2')
rabbitmq2 = factories.rabbitmq('rabbitmq_proc2')


def test_second_rabbitmq(rabbitmq, rabbitmq2):

    print('checking first channel')
    channel = rabbitmq.channel()
    assert channel.state == channel.OPEN

    print('checking second channel')
    channel2 = rabbitmq2.channel()
    assert channel2.state == channel.OPEN


def test_rabbitmq_clear_exchanges(rabbitmq, rabbitmq_proc):
    """
    Declare exchange, and clear it by clear_rabbitmq.
    """
    from rabbitpy import Exchange
    channel = rabbitmq.channel()
    assert channel.state == channel.OPEN

    # list exchanges
    no_exchanges = rabbitmq_proc.list_exchanges()

    # declare exchange and list exchanges afterwards
    exchange = Exchange(channel, 'cache-in')
    exchange.declare()
    exchanges = rabbitmq_proc.list_exchanges()

    # make sure it differs
    assert exchanges != no_exchanges
    clear_rabbitmq(rabbitmq_proc, rabbitmq)

    # list_exchanges again and make sure it's empty
    cleared_exchanges = rabbitmq_proc.list_exchanges()
    assert no_exchanges == cleared_exchanges


def test_rabbitmq_clear_queues(rabbitmq, rabbitmq_proc):
    """
    Declare queue, and clear it by clear_rabbitmq.
    """
    from rabbitpy import Queue
    channel = rabbitmq.channel()
    assert channel.state == channel.OPEN

    # list queues
    no_queues = rabbitmq_proc.list_queues()
    assert not no_queues

    # declare queue, and get new output
    queue = Queue(channel, 'fastlane')
    queue.declare()
    queues = rabbitmq_proc.list_queues()
    assert len(queues) > 0

    # make sure it's different and clear it
    assert queues != no_queues
    clear_rabbitmq(rabbitmq_proc, rabbitmq)

    # list_queues again and make sure it's empty
    cleared_queues = rabbitmq_proc.list_queues()
    assert no_queues == cleared_queues


rabbitmq_rand_proc = factories.rabbitmq_proc(port='?', node_name='test3')
rabbitmq_rand = factories.rabbitmq('rabbitmq_rand_proc')


def test_random_port(rabbitmq_rand):
    """Tests if rabbit fixture can be started on random port"""
    channel = rabbitmq_rand.channel()
    assert channel.state == channel.OPEN


rabbitmq_rand_proc2 = factories.rabbitmq_proc(port='?')
rabbitmq_rand_proc3 = factories.rabbitmq_proc(port='?')


def test_random_port_node_names(rabbitmq_rand_proc2, rabbitmq_rand_proc3):
    """
    Test that rabbitmq_proc fixtures with random ports get different node
    names.
    """
    assert (rabbitmq_rand_proc2.env['RABBITMQ_NODENAME'] !=
            rabbitmq_rand_proc3.env['RABBITMQ_NODENAME'])
