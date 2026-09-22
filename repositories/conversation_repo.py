from datetime import datetime
from repositories import db

#--- Queries ---

CREATE_QUERY = "INSERT INTO conversations (thread_id, title) VALUES (?, ?)"
LIST_ALL_QUERY = "SELECT * FROM conversations ORDER BY updated_at DESC"
GET_QUERY = "SELECT * FROM conversations WHERE thread_id = ?"
EXIST_QUERY = "SELECT 1 FROM conversations WHERE thread_id = ?"
UPDATE_TITLE_QUERY = "UPDATE conversations SET title = ?, updated_at = ? WHERE thread_id = ?"
INCREMEN_MSG_COUNT_QUERY = "UPDATE conversations SET messages_count = messages_count + ?, updated_at = ? WHERE thread_id = ?"
DELETE_QUERY = "DELETE FROM conversations WHERE thread_id = ?"

#--- Functions ---

def create_conversations(thread_id, title):
    with db.get_connection() as conn:
        conn.execute(CREATE_QUERY, (thread_id, title))


def list_all_conversations() -> list[dict]:
    with db.get_connection() as conn:
        rows = conn.execute(LIST_ALL_QUERY).fetchall()

    return [dict(row) for row in rows]

def get_conversation(thread_id) -> dict | None:
     with db.get_connection() as conn:
        row = conn.execute(GET_QUERY, (thread_id,)).fetchone()
        return dict(row) if row else None

def exists_conversation(thread_id) -> bool:
    with db.get_connection() as conn:
        return conn.execute(EXIST_QUERY, (thread_id,)).fetchone() is not None

def update_conversation_title(thread_id, title):
    with db.get_connection() as conn:
        conn.execute(UPDATE_TITLE_QUERY, (title, datetime.now(), thread_id))

def increment_message_count(thread_id, increment = 2):
    with db.get_connection() as conn:
            conn.execute(INCREMEN_MSG_COUNT_QUERY, (increment, datetime.now(), thread_id))

def get_message_count(thread_id) -> int:
    with db.get_connection() as conn:
        row = conn.execute("SELECT messages_count FROM conversations WHERE thread_id = ?", (thread_id,)).fetchone()
        return row["messages_count"] if row else 0

def delete_conversation(thread_id):
    with db.get_connection() as conn:
            conn.execute(DELETE_QUERY, (thread_id))