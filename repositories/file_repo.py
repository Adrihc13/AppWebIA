from datetime import datetime

from repositories.db import get_connection


def create(project_id: str, relative_path: str, content: str) -> None:
    query = "INSERT INTO files (project_id, relative_path, content) VALUES (?, ?, ?)"
    with get_connection() as conn:
        conn.execute(query, (project_id, relative_path, content))


def exists(project_id: str, relative_path: str) -> bool:
    query = "SELECT 1 FROM files WHERE project_id = ? AND relative_path = ?"
    with get_connection() as conn:
        row = conn.execute(query, (project_id, relative_path)).fetchone()

    return row is not None


def get(project_id: str, relative_path: str) -> dict | None:
    query = "SELECT * FROM files WHERE project_id = ? AND relative_path = ?"
    with get_connection() as conn:
        row = conn.execute(query, (project_id, relative_path)).fetchone()

    return dict(row) if row else None


def get_content(project_id: str, relative_path: str) -> str | None:
    file = get(project_id, relative_path)
    return file["content"] if file else None


def get_by_project(project_id: str) -> list[dict]:
    query = "SELECT * FROM files WHERE project_id = ? ORDER BY relative_path ASC"
    with get_connection() as conn:
        rows = conn.execute(query, (project_id,)).fetchall()

    return [dict(row) for row in rows]


def update_documentation(project_id: str, relative_path: str, documentation: str) -> None:
    query = "UPDATE files SET documentation = ?, updated_at = ? WHERE project_id = ? AND relative_path = ?"
    with get_connection() as conn:
        conn.execute(query, (documentation, datetime.now(), project_id, relative_path),)


def delete_by_project(project_id: str) -> None:
    query = "DELETE FROM files WHERE project_id = ?"
    with get_connection() as conn:
        conn.execute(query, (project_id,))