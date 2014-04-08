

def test_elastic_process(elasticsearch_proc):
    """Simple test for starting elasticsearch_proc."""
    assert elasticsearch_proc.running() is True


def test_elasticsarch(elasticsearch):
    """Tests if elasticsearch fixtures connects to process."""

    info = elasticsearch.info()

    assert info['status'] == 200
