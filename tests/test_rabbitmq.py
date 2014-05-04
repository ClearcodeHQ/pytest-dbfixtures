from pytest_dbfixtures import factories


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
