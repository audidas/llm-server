from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from beanie import Document
from pydantic import UUID4, Field, TypeAdapter

from app.util import kst_now


class Documents(Document):
    url: str
    title: str
    content: str
    message_id: UUID4
    date: Optional[str]

    id: UUID4 = Field(default_factory=uuid4)
    deprecated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=kst_now)


document_adapter = TypeAdapter(List[Documents])
