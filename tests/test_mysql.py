def test_mysql(mysqldb):

    cursor = mysqldb.cursor()
    cursor.execute("SELECT CURRENT_USER()")
    results = cursor.fetchall()

    assert len(results) == 1
