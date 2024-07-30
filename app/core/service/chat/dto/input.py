from typing import Optional, Any
from fastapi import WebSocket
from pydantic import BaseModel, UUID4


class KnowledgeFirstChat(BaseModel):
    user_id: str
    content: str
    root_id: UUID4
    message_id: UUID4


class KnowledgeChat(BaseModel):
    user_id: str
    model: str
    content: str
    parent_id: UUID4
    message_id: UUID4
    conversation_id: UUID4
    websocket: Any


class MapFirstChat(BaseModel):
    user_id: str
    content: str

    geometry: str
    image_path: str

    root_id: UUID4
    message_id: UUID4


class MapChat(BaseModel):
    user_id: str
    model: str
    context: Optional[dict]
    content: str

    parent_id: UUID4
    message_id: UUID4
    conversation_id: UUID4
    websocket: Any
