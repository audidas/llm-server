from typing import List, Dict, Optional
from uuid import uuid4

from beanie import Document
from pydantic import UUID4, Field


class Command(Document):
    id: UUID4 = Field(default_factory=uuid4)
    message_id: UUID4
    commands: Optional[List[dict]]
