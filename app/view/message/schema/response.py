from beanie import PydanticObjectId
from pydantic import BaseModel, UUID4


class MessageConversationWriter(BaseModel):
    role: str
    user_id: PydanticObjectId
    message_id: UUID4
    conversation_id: UUID4
