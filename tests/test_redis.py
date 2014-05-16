from pytest_dbfixtures import factories


def test_redis(redisdb):
    redisdb.set('test1', 'test')
    redisdb.set('test2', 'test')

    test1 = redisdb.get('test1')
    assert test1 == 'test'

    test2 = redisdb.get('test2')
    assert test2 == 'test'


redis2_params = '--save "" --rdbcompression no --rdbchecksum no'
redis_proc2 = factories.redis_proc(port=6381, params=redis2_params)
redisdb2 = factories.redisdb('redis_proc2', port=6381)


def test_second_redis(redisdb, redisdb2):
    redisdb.set('test1', 'test')
    redisdb.set('test2', 'test')
    redisdb2.set('test1', 'test_other')
    redisdb2.set('test2', 'test_other')

    test1 = redisdb.get('test1')
    assert test1 == 'test'

    test2 = redisdb.get('test2')
    assert test2 == 'test'

    assert redisdb2.get('test1') == 'test_other'
    assert redisdb2.get('test2') == 'test_other'
