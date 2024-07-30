from datetime import datetime
from typing import List, Union, Optional

from beanie import Document
from pydantic import UUID4, BaseModel, field_serializer

from pydantic import TypeAdapter


class Prompt(Document):
    message_id: Optional[UUID4]
    messages: List["Message"]
    documents: List["Documents"]

    class Message(BaseModel):
        role: str
        content: str

    class Documents(BaseModel):
        title: str
        content: str
        date: Union[str, datetime]
        url: str

        @field_serializer("date")
        def str_to_datetime(self, dt: str, _info):
            return datetime.strptime(dt, "%Y%m%d")


message_adapter = TypeAdapter(List[Prompt.Message])
documents_adapter = TypeAdapter(List[Prompt.Documents])
