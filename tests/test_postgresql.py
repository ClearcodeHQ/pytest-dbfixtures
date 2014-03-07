from pytest_dbfixtures import factories

query = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"

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
