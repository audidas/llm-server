from datetime import datetime

from beanie import Document, BeanieObjectId, Indexed
from pydantic import UUID4, Field

from app.util import kst_now


class PreSignedUrl(Document):
    user_id: BeanieObjectId
    document_id: UUID4
    url: str
    generated_at: Indexed(datetime, expireAfterSeconds=3600) = Field(default_factory=kst_now)
