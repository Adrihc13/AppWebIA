from datetime import datetime
from repositories import db


#--- Functions ---

CREATE_QUERY = "INSERT INTO conversations (thread_id, title, file_path) VALUES (?, ?, ?)"
def create_conversations(thread_id, title, file_path: str | None = None):
    with db.get_connection() as conn:
        conn.execute(CREATE_QUERY, (thread_id, title, file_path))


LIST_ALL_QUERY = "SELECT * FROM conversations ORDER BY updated_at DESC"
def list_all_conversations() -> list[dict]:
    with db.get_connection() as conn:
        rows = conn.execute(LIST_ALL_QUERY).fetchall()

    return [dict(row) for row in rows]

GET_QUERY = "SELECT * FROM conversations WHERE thread_id = ?"
def get_conversation(thread_id) -> dict | None:
     with db.get_connection() as conn:
        row = conn.execute(GET_QUERY, (thread_id,)).fetchone()
        return dict(row) if row else None

EXIST_QUERY = "SELECT 1 FROM conversations WHERE thread_id = ?"
def exists_conversation(thread_id) -> bool:
    with db.get_connection() as conn:
        return conn.execute(EXIST_QUERY, (thread_id,)).fetchone() is not None

IS_NEW_CONVERSATION_QUERY = "SELECT file_path, messages_count FROM conversations WHERE thread_id = ?"
def is_new_conversation(thread_id: str) -> bool:
    with db.get_connection() as conn:
        row = conn.execute(IS_NEW_CONVERSATION_QUERY,(thread_id,)).fetchone()

    if row is None:
        return False   # no existe → no es "nueva", no aplica

    file_path = row["file_path"]
    message_count = row["messages_count"]

    return file_path is None and message_count == 0

UPDATE_TITLE_QUERY = "UPDATE conversations SET title = ?, file_path = ?, updated_at = ? WHERE thread_id = ?"
def update_conversation_title_and_file(thread_id, title, file_path: str | None = None):
    with db.get_connection() as conn:
        conn.execute(UPDATE_TITLE_QUERY, (title, file_path, datetime.now(), thread_id))

INCREMEN_MSG_COUNT_QUERY = "UPDATE conversations SET messages_count = messages_count + ?, updated_at = ? WHERE thread_id = ?"
def increment_message_count(thread_id, increment = 2):
    with db.get_connection() as conn:
            conn.execute(INCREMEN_MSG_COUNT_QUERY, (increment, datetime.now(), thread_id))

def get_message_count(thread_id) -> int:
    with db.get_connection() as conn:
        row = conn.execute("SELECT messages_count FROM conversations WHERE thread_id = ?", (thread_id,)).fetchone()
        return row["messages_count"] if row else 0

DELETE_QUERY = "DELETE FROM conversations WHERE thread_id = ?"
def delete_conversation(thread_id):
    with db.get_connection() as conn:
            conn.execute(DELETE_QUERY, (thread_id,))