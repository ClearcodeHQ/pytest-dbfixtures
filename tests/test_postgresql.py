import pytest
from pytest_dbfixtures import factories

query = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"

postgresql91 = factories.postgresql_proc(
    '/usr/lib/postgresql/9.1/bin/pg_ctl', port=9877)
postgresql92 = factories.postgresql_proc(
    '/usr/lib/postgresql/9.2/bin/pg_ctl', port=9878)
postgresql93 = factories.postgresql_proc(
    '/usr/lib/postgresql/9.3/bin/pg_ctl', port=9879)


@pytest.mark.parametrize('postgres',
                         ('postgresql91', 'postgresql92', 'postgresql93',))
def test_postgresql_proc(request, postgres):
    postgresql_proc = request.getfuncargvalue(postgres)
    assert postgresql_proc.running() is True


def test_postgres(postgresql):
    cur = postgresql.cursor()
    cur.execute(query)
    postgresql.commit()
    cur.close()


postgresql_proc2 = factories.postgresql_proc(port=9876)
postgresql2 = factories.postgresql('postgresql_proc2', port=9876)


def test_two_postgreses(postgresql, postgresql2):
    cur = postgresql.cursor()
    cur.execute(query)
    postgresql.commit()
    cur.close()

    cur = postgresql2.cursor()
    cur.execute(query)
    postgresql2.commit()
    cur.close()
