from pytest_dbfixtures import factories


def test_elastic_process(elasticsearch_proc):
    """Simple test for starting elasticsearch_proc."""
    assert elasticsearch_proc.running() is True


def test_elasticsarch(elasticsearch):
    """Tests if elasticsearch fixtures connects to process."""

    info = elasticsearch.info()
    assert info['status'] == 200


elasticsearch_proc_random = factories.elasticsearch_proc(port='?')
elasticsearch_random = factories.elasticsearch('elasticsearch_proc_random')


def test_random_port(elasticsearch_random):
    """Tests if elasticsearch fixture can be started on random port"""
    assert elasticsearch_random.info()['status'] == 200
