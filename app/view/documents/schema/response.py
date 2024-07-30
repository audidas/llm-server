from datetime import datetime
from typing import List, Annotated, Union

from pydantic import BaseModel, UUID4, PlainSerializer, TypeAdapter, ConfigDict, Field

from app.view.serialize import created_at_serializer


class DocumentElement(BaseModel):
    document_id: UUID4 = Field(validation_alias='id')
    message_id: UUID4
    url: str
    title: str
    content: str
    deprecated: bool
    created_at: Annotated[
        Union[str, datetime],
        PlainSerializer(created_at_serializer)
    ]

    model_config = ConfigDict(populate_by_name=True)


document_res_adapter = TypeAdapter(List[DocumentElement])


class DocumentListResponse(BaseModel):
    document_list: List[DocumentElement]
