import json
import os
from datetime import datetime
from typing import List, Dict
from uuid import uuid4

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import pooling

load_dotenv()
# Create a connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="pool",
    pool_size=10,
    pool_reset_session=True,
    raise_on_warnings=True,
    host=os.getenv('AITOOLS_CHAT_DB_HOST'),
    database=os.getenv('AITOOLS_CHAT_DB_NAME'),
    user=os.getenv('AITOOLS_CHAT_DB_USER'),
    password=os.getenv('AITOOLS_CHAT_DB_PASSWORD'),
    port=os.getenv('AITOOLS_CHAT_DB_PORT')
)


from datetime import datetime
import json
from typing import List, Dict
import mysql.connector

from datetime import datetime
import json
from typing import List, Dict
import mysql.connector

def save_conversation(conversation_id: str, user: str, organization: str, model: str, messages: List[Dict[str, str]]):
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = """
                INSERT INTO conversations (conversation_id, user, organization, model, messages, created_ts)
                VALUES (%s, %s, %s, %s, %s, %s) AS new
                ON DUPLICATE KEY UPDATE
                    user = new.user,
                    organization = new.organization,
                    model = new.model,
                    messages = new.messages,
                    created_ts = new.created_ts
            """
            cursor.execute(query, (conversation_id, user, organization, model, json.dumps(messages), datetime.now()))
            connection.commit()
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()




def create_new_conversation_id(user: str, organization: str, model: str) -> str:
    conversation_id = str(uuid4())
    # Optionally, you can save the initial conversation metadata here
    return conversation_id

def conversation_by_id(conversation_id: str) -> Dict[str, any]:
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """SELECT conversation_id, user, organization, model, messages, created_ts
                       FROM conversations WHERE conversation_id = %s"""
            cursor.execute(query, (conversation_id,))
            result = cursor.fetchone()
            if result:
                result['messages'] = json.loads(result['messages'])
                return result
            else:
                return None
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def conversations_by_user(username: str = None) -> List[Dict[str, any]]:
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            if username:
                query = """SELECT conversation_id, user, organization, model, messages, created_ts
                           FROM conversations WHERE user = %s ORDER BY created_ts DESC"""
                cursor.execute(query, (username,))
                results = cursor.fetchall()
            else:
                results = []

            for result in results:
                result['messages'] = json.loads(result['messages'])
            return results
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def delete_conversation(user, conversation_id):
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = """DELETE FROM conversations WHERE user = %s AND conversation_id = %s"""
            cursor.execute(query, (user, conversation_id))
            connection.commit()
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
