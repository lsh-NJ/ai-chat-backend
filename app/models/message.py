from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Message:
    id: int
    coversation_id: int
    role: str
    content: str
    created_at: str
