from pytest_dbfixtures import factories
from pytest_dbfixtures.factories.rabbitmq import clear_rabbitmq


def test_rabbitmq(rabbitmq):
    channel = rabbitmq.channel()
    assert channel.is_open


rabbitmq_proc2 = factories.rabbitmq_proc(port=5674, node_name='rabbitmqtest2')
rabbitmq2 = factories.rabbitmq('rabbitmq_proc2', port=5674)


def test_second_rabbitmq(rabbitmq, rabbitmq2):

    print 'checking first channel'
    channel = rabbitmq.channel()
    assert channel.is_open

    print 'checking second channel'
    channel2 = rabbitmq2.channel()
    assert channel2.is_open


def test_rabbitmq_clear_exchanges(rabbitmq, rabbitmq_proc):
    """
    Declare exchange, and clear it by clear_rabbitmq.
    """
    channel = rabbitmq.channel()
    assert channel.is_open

    # list exchanges
    no_exchanges = rabbitmq_proc.list_exchanges()

    # declare exchange and list exchanges afterwards
    channel.exchange_declare(exchange='cache-in')
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
    channel = rabbitmq.channel()
    assert channel.is_open

    # list queues
    no_queues = rabbitmq_proc.list_queues()
    assert not no_queues

    # declare queue, and get new output
    channel.queue_declare(queue='fastlane')
    queues = rabbitmq_proc.list_queues()
    assert len(queues) > 0

    # make sure it's different and clear it
    assert queues != no_queues
    clear_rabbitmq(rabbitmq_proc, rabbitmq)

    # list_queues again and make sure it's empty
    cleared_queues = rabbitmq_proc.list_queues()
    assert no_queues == cleared_queues
