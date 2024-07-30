from typing import Optional
from uuid import uuid4
from datetime import datetime

from beanie import Document
from pydantic import UUID4, Field

from app.util import kst_now


class Message(Document):
    role: str
    content: str
    model: str = Field(default='model not necessary')
    conversation_id: UUID4
    parent_id: Optional[UUID4]
    children: list[UUID4] = Field(default_factory=list)
    id: UUID4 = Field(default_factory=uuid4)
    feedback: int = Field(ge=-1, le=1, default=0)
    created_at: datetime = Field(default_factory=kst_now)

    class Settings:
        use_state_management = True

    async def append_children(self, message: "Message"):
        self.children.append(str(message.id))
        await self.save_changes()
