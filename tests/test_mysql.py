def select_current_user(cursor):
    cursor.execute("SELECT CURRENT_USER()")
    results = cursor.fetchall()
    cursor.close()
    return results


def test_mysql(mysqldb):
    results = select_current_user(mysqldb.cursor())
    assert len(results) == 1


def test_mysql_session(mysqldb_session):
    results = select_current_user(mysqldb_session.cursor())
    assert len(results) == 1
