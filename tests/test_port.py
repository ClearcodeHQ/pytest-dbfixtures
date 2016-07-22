import pytest

import port_for

from pytest_dbfixtures.port import get_port


@pytest.mark.parametrize('ports, ports_set', (
    (2000, 2000),
    ('2000', 2000),
    (set([2000]), 2000),
    ({3000, 3001, 3005}, (3000, 3001, 3005)),
    ([{2001, 2002}], (2001, 2002)),
    ([{2001, 2004, 2005}], (2001, 2004, 2005)),
    ([(2001, 2004), (2002, 2006)], (2001, 2002, 2003, 2004, 2005, 2006)),
    ([(2001, 2003), {2005, 2007}], (2001, 2002, 2003, 2005, 2007)),
    ([(2001, 2003), {2005}, (2009, 2010)], (
        2001, 2002, 2003, 2005, 2009, 2010)),
    ([(2001, 2004), {3000, 3005, 3009}, 345, 349, 404],
        (2001, 2002, 2003, 2004, 3000, 3005, 3009, 345, 349, 404))
))
def test_ports_parsing(ports, ports_set):

    try:
        port = get_port(ports)
        assert port == ports_set or port in ports_set
    except port_for.exceptions.PortForException:
        pass  # it may happen that some of the ports are already in use


@pytest.mark.parametrize('ports', (
    '21.32',
    '12--100',
    '12,30,400-300',
    'a,32,2',
))
def test_ports_invalid_def(ports):
    with pytest.raises(ValueError) as excinfo:
        get_port(ports)
    assert ports in str(excinfo)


@pytest.mark.parametrize('ports', (
    '',
    [],
    set(),
    {},
))
def test_ports_returns_none(ports):
    assert get_port(ports) is not None


def test_random_port_exception(request, redis_proc, postgresql_proc):
    """
    Check if PortForException is raised when we try to start
    next fixture on already used ports.
    """

    with pytest.raises(port_for.exceptions.PortForException):
        ports = [{redis_proc.port, postgresql_proc.port}]
        get_port(ports)
