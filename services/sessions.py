import os
from datetime import datetime, timedelta
import uuid
from typing import Optional
from mysql.connector import pooling
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MySQL connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="session_pool",
    pool_size=10,
    pool_reset_session=True,
    raise_on_warnings=True,
    host=os.getenv('AITOOLS_CHAT_DB_HOST'),
    database=os.getenv('AITOOLS_CHAT_DB_NAME'),
    user=os.getenv('AITOOLS_CHAT_DB_USER'),
    password=os.getenv('AITOOLS_CHAT_DB_PASSWORD'),
    port=os.getenv('AITOOLS_CHAT_DB_PORT')
)

# Constants
SESSION_TIMEOUT_MINUTES = 30
IDLE_TIMEOUT_MINUTES = 10


def create_session(username: str) -> tuple[str, str] | tuple[None, None]:
    """Create a new session for a user."""
    session_id = str(uuid.uuid4())
    session_key = str(uuid.uuid4())
    now = datetime.now()
    expiry = now + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = """
                INSERT INTO chat_sessions (session_id, username, session_key, last_active, expiry)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (session_id, username, session_key, now, expiry))
            connection.commit()
            return session_id, session_key
    except Exception as e:
        print(f"Error creating session: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    return None, None


def validate_session(session_id: str, session_key: str) -> bool:
    """Validate a session's existence and expiry."""
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT * FROM chat_sessions WHERE session_id = %s AND session_key = %s
            """
            cursor.execute(query, (session_id, session_key))
            session = cursor.fetchone()
            if session:
                now = datetime.now()
                expiry = session['expiry']
                last_active = session['last_active']

                # Check expiry and idle timeout
                if now > expiry or now - last_active > timedelta(minutes=IDLE_TIMEOUT_MINUTES):
                    delete_session(session_id)
                    return False

                # Update last active timestamp
                update_last_active(session_id)
                return True
    except Exception as e:
        print(f"Error validating session: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    return False


def update_last_active(session_id: str):
    """Update the last active timestamp for a session."""
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = "UPDATE chat_sessions SET last_active = %s WHERE session_id = %s"
            cursor.execute(query, (datetime.now(), session_id))
            connection.commit()
    except Exception as e:
        print(f"Error updating last active timestamp: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def delete_session(session_id: str):
    """Delete a session."""
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            query = "DELETE FROM chat_sessions WHERE session_id = %s"
            cursor.execute(query, (session_id,))
            connection.commit()
    except Exception as e:
        print(f"Error deleting session: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def session_info(session_id: str) -> Optional[dict]:
    """Retrieve session information."""
    connection = None
    cursor = None
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT session_id, username, session_key, last_active, expiry
                FROM chat_sessions WHERE session_id = %s
            """
            cursor.execute(query, (session_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error retrieving session info: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    return None
