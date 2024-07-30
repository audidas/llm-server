from datetime import datetime
from uuid import uuid4

from pydantic import UUID4, Field
from beanie import Document, PydanticObjectId

from app.util import kst_now


class Conversation(Document):
    id: UUID4 = Field(default_factory=uuid4)
    user_id: PydanticObjectId
    mode: str
    deprecated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=kst_now)

    @property
    def user_id_str(self):
        return str(self.user_id)
