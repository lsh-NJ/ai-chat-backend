from app.models.message import Message
from app.db.database import get_connection, now_iso


# 存储信息：
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


# 获得相应会话的所有信息
def list_message(coversation_id: int) -> list[Message]:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (coversation_id,),
        )

        rows = cursor.fetchall()

    return [
        Message(
            id=row["id"],
            coversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        )

        for row in rows
    ]


# 查询会话的近 10 条对话
def list_recent_messages(
    conversation_id: int,
    limit: int = 20,
) -> list[dict[str, str]]:
    with get_connection() as conn:
        # 倒序排序意味着查询 id 更大（最近）的对话
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

    # reversed 返回的是 list_reverseiterator，使用 list() 进行转换
    rows = list(reversed(rows)) 

    return [
        Message(
            id=row["id"],
            coversation_id=row["conversation_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        )

        for row in rows
    ]

