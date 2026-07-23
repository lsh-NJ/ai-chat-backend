import sqlite3
from app.db.database import get_connection, now_iso
from app.models.conversation import Conversation

'''
负责SQL
'''

# 数据库转 Conversation
def _to_conversation(row: sqlite3.Row) -> Conversation:
    return Conversation(
        id=row["id"],
        title=row["title"],
        created_at=row["create_at"],
    )


# 创建
def create(title: int | None = None) -> int:
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


# 获取当前会话信息
def get_by_id(conversation_id: int) -> Conversation | None:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECTE id, title, created_at
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return _to_conversation(row)


# 获取会话列表：
def list_all() -> list[Conversation]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, title, created_at
            FROM conversations
            ORDER BY ID DESC
            """
        )

        rows = cursor.fetchall()

    return [_to_conversation(row) for row in rows]
    