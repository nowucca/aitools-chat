from typing import List, Dict
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
import hashlib
from dotenv import load_dotenv

load_dotenv()
# Create a connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    pool_reset_session=True,
    host='aitools.cs.vt.edu',
    database='aitools_chat',
    user='',
    password='your_password'
)

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()

def get_latest_message_hash(user: str) -> str:
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = """SELECT message_hash FROM conversations
                       WHERE user = %s
                       ORDER BY created_ts DESC LIMIT 1"""
            cursor.execute(query, (user,))
            result = cursor.fetchone()
            return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def save_conversation(user: str, messages: List[Dict[str, str]]):
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = """INSERT INTO conversations (user, role, content, created_ts, message_hash)
                       VALUES (%s, %s, %s, %s, %s)"""
            check_query = "SELECT 1 FROM conversations WHERE message_hash = %s"

            latest_hash = get_latest_message_hash(user)
            save_messages = False if latest_hash else True

            for message in messages:
                content = message["content"]
                message_hash = compute_hash(content)
                if save_messages:
                    cursor.execute(check_query, (message_hash,))
                    if cursor.fetchone() is None:
                        cursor.execute(query, (user, message["role"], content, datetime.now(), message_hash))
                elif message_hash == latest_hash:
                    save_messages = True

            connection.commit()

    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
