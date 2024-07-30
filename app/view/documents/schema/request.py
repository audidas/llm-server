from typing import List, Optional

from pydantic import BaseModel


class CreateDocumentRequest(BaseModel):
    document_list: List["DocumentElement"]

    class DocumentElement(BaseModel):
        url: str
        title: str
        content: str
        date: Optional[str]
