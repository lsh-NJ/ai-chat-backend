import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

# 返回标准的格式化时间
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# 返回数据库连接
def get_connection() -> sqlite3.Connection:
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id)
            )
            """
        )

        conn.commit()


def create_conversation(title: str | None = None) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO conversations (title, created_at)
            VALUES (?, ?)
            """,
            (title, now_iso()),
        )
        conn.commit()

        return int(cursor.lastrowid)


def get_conversation(conversation_id: int) -> sqlite3.Row | None:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        )

        return cursor.fetchone()


def save_message(
    conversation_id: int,
    role: str,
    content: str,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, content, now_iso()),
        )
        conn.commit()

        return int(cursor.lastrowid)


# 获得会话信息
def list_conversations() -> list[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()


# 获得相应会话的所有信息
def list_messages(conversation_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        )

        return cursor.fetchall()

# 查询相应会话最近若干条信息
def list_recent_messages_for_llm(
    conversation_id: int,
    limit: int = 20,
) -> list[dict[str, str]]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        )

        rows = cursor.fetchall()

    rows = list(reversed(rows))

    return [
        {
            "role": row["role"],
            "content": row["content"],
        }
        for row in rows
    ]