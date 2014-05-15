from pytest_dbfixtures import factories

query = '''CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20),
    species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);'''


def test_proc(mysql_proc):
    assert mysql_proc.running()
    pass


def test_mysql(mysqldb):
    cursor = mysqldb.cursor()
    cursor.execute(query)
    mysqldb.commit()
    cursor.close()


mysql_proc2 = factories.mysql_proc(port=3308, params='--skip-sync-frm')
mysqldb2 = factories.mysqldb('mysql_proc2', port=3308)


def test_mysql_newfixture(mysqldb, mysqldb2):
    cursor = mysqldb.cursor()
    cursor.execute(query)
    mysqldb.commit()
    cursor.close()

    cursor = mysqldb2.cursor()
    cursor.execute(query)
    mysqldb2.commit()
    cursor.close()
