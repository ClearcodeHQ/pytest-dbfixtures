from io import StringIO

import pytest
import mock

from pytest_dbfixtures import factories
from pytest_dbfixtures.factories.redis import RedisUnsupported
from pytest_dbfixtures.utils import extract_version, compare_version


def test_redis(redisdb):
    redisdb.set('test1', 'test')
    redisdb.set('test2', 'test')

    test1 = redisdb.get('test1')
    assert test1 == 'test'

    test2 = redisdb.get('test2')
    assert test2 == 'test'


redis2_params = '--save "" --rdbcompression no --rdbchecksum no'
redis_proc2 = factories.redis_proc(port=6381, params=redis2_params)
redisdb2 = factories.redisdb('redis_proc2')


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


redis_proc_random = factories.redis_proc(port=None)
redisdb_random = factories.redisdb('redis_proc_random')


def test_random_port(redisdb_random):
    """Tests if redis fixture can be started on random port"""
    assert redisdb_random.keys('*') == []


redis_proc_to_mock = factories.redis_proc(port=None)


@pytest.mark.parametrize('version', (
    u'Redis server version 2.4.14 (e9935407:0)',
    u'Redis server version 2.4.13 (e0935407:0)'
    u'Redis server version 2.5.0 (e9035407:0)'
    u'Redis server version 2.3.10 (e9933407:0)'
))
def test_old_redis(request, version):
    """Tests how fixture behaves in case of old redis version"""
    with mock.patch(
            'os.popen',
            lambda *args: StringIO(version)
    ):
        with pytest.raises(RedisUnsupported):
            request.getfuncargvalue('redis_proc_to_mock')


@pytest.mark.parametrize("versions,result", [
    (["2.8.18", "2.6"], 1),
    (["2.4.14", "2.6"], -1),
    (["2.6.0", "2.6"], 0),
    (["3.0.0", "2.6.17"], 1),
    (["2.6.1", "2.6.17"], -1),
])
def test_compare_version(versions, result):
    assert compare_version(versions[0], versions[1]) == result


@pytest.mark.parametrize("text,result", [
    ("Redis server version 2.4.14 (00000000:0)", "2.4.14"),
    ("Redis server v=2.6.13 sha=00000000:0 malloc=jemalloc-3.3.1 bits=64",
     "2.6.13"),
    ("1.2.5", "1.2.5"),
    ("Test2.0.5", "2.0.5"),
    ("2.0.5Test", "2.0.5"),
    ("Test", None),
    ("m.n.a 2.4.14", "2.4.14")
])
def test_extract_version(text, result):
    assert extract_version(text) == result
