import pytest

import port_for

from pytest_dbfixtures.port import (
    parse_ports,
    get_port,
    InvalidPortsDefinition,
)


@pytest.mark.parametrize('ports, ports_set', (
    ('?', None),
    ('2000', set([2000])),
    ('2001-2002', set([2001, 2002])),
    ('2001,2004,2005', set([2001, 2004, 2005])),
    ('2001-2004,2002-2006', set([2001, 2002, 2003, 2004, 2005, 2006])),
    ('2001-2003,2005,2007', set([2001, 2002, 2003, 2005, 2007])),
    ('2001-2003,2005,2009-2010', set([2001, 2002, 2003, 2005, 2009, 2010])),
))
def test_ports_parsing(ports, ports_set):
    assert parse_ports(ports) == ports_set

    try:
        port = get_port(ports)
        if ports_set:
            assert port in ports_set
    except port_for.exceptions.PortForException:
        pass  # it may happen that some of the ports are already in use


@pytest.mark.parametrize('ports, ports_set', (
    ('2000', 2000),
    (2000, 2000),
))
def test_ports_parsing_passthrough(ports, ports_set):
    assert get_port(ports) == ports_set


@pytest.mark.parametrize('ports', (
    '21.32',
    '12--100',
    '12,30,400-300',
    'a,32,2',
))
def test_ports_invalid_def(ports):
    with pytest.raises(InvalidPortsDefinition) as excinfo:
        get_port(ports)
    assert ports in str(excinfo)


def test_random_port_exception(request, redis_proc, postgresql_proc):
    """
    Check if PortForException is raised when we try to start
    next fixture on already used ports.
    """

    with pytest.raises(port_for.exceptions.PortForException):
        get_port('%s,%s' % (redis_proc.port, postgresql_proc.port))
