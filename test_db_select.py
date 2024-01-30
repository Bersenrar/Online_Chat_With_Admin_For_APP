import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="renologankpp23",
    autocommit=True,
    database="chatdatabase"
)

cursor = conn.cursor()

cursor.execute("SELECT * FROM MESSAGES;")

print(cursor.fetchall())

cursor.close()
conn.close()


