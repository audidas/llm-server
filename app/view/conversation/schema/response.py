from datetime import datetime
from typing import List, Annotated, Union, Optional, Dict

from pydantic import BaseModel, UUID4, PlainSerializer, ConfigDict, Field

from app.view.conversation.schema.request import Mode
from app.view.serialize import created_at_serializer


class PreviewElement(BaseModel):
    mode: Mode
    conversation_id: UUID4
    last_content: Optional[str] = Field(default=None)
    message_id: Optional[UUID4] = Field(default=None)
    last_timestamp: Optional[
        Annotated[datetime, PlainSerializer(lambda x: x.strftime("%Y.%m.%d %H:%M"))]
    ] = Field(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )


class ConversationPreviewResponse(BaseModel):
    chat_list: List[PreviewElement]


#############


class ConversationDocuments(BaseModel):
    message_id: UUID4
    document_id: UUID4
    created_at: Annotated[Union[str, datetime], PlainSerializer(created_at_serializer)]
    deprecated: bool

    url: str
    title: str
    content: str


#############


class DocumentElement(BaseModel):
    document_id: UUID4 = Field(validation_alias="_id")
    created_at: Annotated[Union[str, datetime], PlainSerializer(created_at_serializer)]
    deprecated: bool

    url: str
    title: str
    content: str


class MessageIncludeDocs(BaseModel):
    message_id: UUID4
    message: "MessageElement"
    documents: List[DocumentElement]
    created_at: Annotated[datetime, PlainSerializer(lambda x: x.strftime("%Y.%m.%d"))]

    class MessageElement(BaseModel):
        role: str
        content: str
        parent_id: Optional[UUID4]
        children: Optional[List[UUID4]]


class ContextResponse(BaseModel):
    user_id: str
    created_at: Annotated[datetime, PlainSerializer(lambda x: x.strftime("%Y.%m.%d"))]
    conversation_id: UUID4
    messages: List[MessageIncludeDocs]


class MapContextResponse(ContextResponse):
    commands: List[Dict]
