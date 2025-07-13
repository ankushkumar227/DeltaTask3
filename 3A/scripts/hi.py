import mysql.connector
from mysql.connector import Error

try:
    myconn = mysql.connector.connect(
        host='mysql-service',
        user='Ankush',
        password='Elon@2005',
        database='chatServer'
    )
    if myconn.is_connected():
        print("✅ Connected to MySQL!")

        # Create cursor
        cursor = myconn.cursor()

        # Run a test query
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📦 Tables in chatServer DB:")
        for table in tables:
            print(table)

        # Clean up
        cursor.close()
        myconn.close()
except Error as e:
    print("❌ Error:", e)
