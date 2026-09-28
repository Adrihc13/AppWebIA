from datetime import date
from repositories.db import get_connection


def create(project_id: str, name: str, path: str = "") -> None:
    query = "INSERT INTO projects (id, name, path) VALUES (?, ?, ?)"

    with get_connection() as conn:
        conn.execute(query, (project_id, name, path,))

def get(project_id: str) -> dict:
    query = "SELECT * FROM projects WHERE id = ?"
    with get_connection() as conn:
        row = conn.execute(query,(project_id,),)
    
    return dict(row) if row else None

def get_all() -> list[dict]:
    query = "SELECT * FROM projects ORDER BY created_at DESC"
    with get_connection() as conn:
        rows = conn.execute(query,).fetchall()
    
    return [dict(row) for row in rows]

def exist(project_id: str) -> bool:
    query = "SELECT 1 FROM projects WHERE id = ?"
    with get_connection() as conn:
        row = conn.execute(query, (project_id,),).fetchone()

    return row is not None

def delete(project_id: str) -> None:
    query = "DELETE FROM projects WHERE id = ?"
    with get_connection() as conn:
        conn.execute( query, (project_id,),)

