def test_mysql(mysqldb):

    mysqldb.execute("SELECT CURRENT_USER()")
    results = mysqldb.fetchall()

    assert len(results) == 1
