from dataclasses import dataclass

@dataclass(slots=True, frozen=True)
class Conversation:
    id: int
    title: str | None
    created_at: str