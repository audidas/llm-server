from enum import Enum

from pydantic import BaseModel, UUID4


class Mode(str, Enum):
    map = "map"
    knowledge = "knowledge"


class Model(str, Enum):
    satllm = "satllm"
    chatgpt = "chatgpt"
    dummy = "dummy"


class KnowledgeFirstRequest(BaseModel):
    content: str
    root_id: UUID4
    message_id: UUID4


class KnowledgeRequest(BaseModel):
    content: str
    parent_id: UUID4
    message_id: UUID4


class MapContext(BaseModel):
    image_path: str
    geometry: str


class MapFirstRequest(BaseModel):
    content: str
    root_id: UUID4
    message_id: UUID4
    context: MapContext


class MapRequest(BaseModel):
    content: str
    parent_id: UUID4
    message_id: UUID4
    context: MapContext
