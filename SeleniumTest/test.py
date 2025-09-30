import MySQLdb

conn = MySQLdb.connect(
    user="crawl_test_user",
    passwd="TEST001",
    host="localhost",
    db="crawl_test"
    # charset="utf-8"
)
print(type(conn))
# <class 'MySQLdb.connections.Connection'>
cursor = conn.cursor()
print(type(cursor))
# <class 'MySQLdb.cursors.Cursor'>
cursor.execute("CREATE TABLE books (title text, url text)")
conn.commit()
