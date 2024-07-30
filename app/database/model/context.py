from uuid import uuid4
from pydantic import Field

from beanie import Document
from pydantic import UUID4
from typing import Optional


class Context(Document):
    id: UUID4 = Field(default_factory=uuid4)
    message_id: UUID4
    context: Optional[dict]

    @staticmethod
    async def query_by_message_id(message_id):
        context = await Context.find_one(Context.message_id == message_id)
        print(context)
        return context.context
