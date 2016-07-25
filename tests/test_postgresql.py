import psycopg2
import pytest

from pytest_dbfixtures import factories


query = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"

pg_ctl = '/usr/lib/postgresql/{ver}/bin/pg_ctl'

postgresql91 = factories.postgresql_proc(pg_ctl.format(ver='9.1'), port=9877)
postgresql92 = factories.postgresql_proc(pg_ctl.format(ver='9.2'), port=9878)
postgresql93 = factories.postgresql_proc(pg_ctl.format(ver='9.3'), port=9879)


@pytest.mark.parametrize('postgres', (
    'postgresql91',
    'postgresql92',
    'postgresql93',
))
def test_postgresql_proc(request, postgres):
    postgresql_proc = request.getfuncargvalue(postgres)
    assert postgresql_proc.running() is True


def test_main_postgres(postgresql):
    cur = postgresql.cursor()
    cur.execute(query)
    postgresql.commit()
    cur.close()


postgresql_proc2 = factories.postgresql_proc(port=9876)
postgresql2 = factories.postgresql('postgresql_proc2')


def test_two_postgreses(postgresql, postgresql2):
    cur = postgresql.cursor()
    cur.execute(query)
    postgresql.commit()
    cur.close()

    cur = postgresql2.cursor()
    cur.execute(query)
    postgresql2.commit()
    cur.close()


postgresql_rand_proc = factories.postgresql_proc(port=None)
postgresql_rand = factories.postgresql('postgresql_rand_proc')


def test_rand_postgres_port(postgresql_rand):
    """Tests if postgres fixture can be started on random port"""
    assert postgresql_rand.status == psycopg2.extensions.STATUS_READY
