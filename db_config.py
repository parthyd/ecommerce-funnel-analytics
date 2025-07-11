import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Yadav1199@',  # Replace with the password you set
            database='ecommerce_db'
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None
