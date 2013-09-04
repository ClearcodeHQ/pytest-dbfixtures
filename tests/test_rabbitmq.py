def test_rabbitmq(rabbitmq):
    channel = rabbitmq.channel()
    assert channel.is_open
