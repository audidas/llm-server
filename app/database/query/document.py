from datetime import datetime
from typing import List

from pydantic import UUID4

from app.database import Prompt, Documents


async def save_documents_from_prompt(prompt: Prompt):
    documents: List[Prompt.Documents] = prompt.documents

    for doc in documents:
        await Documents(
            url=doc.url,
            title=doc.title,
            content=doc.content,
            message_id=prompt.message_id,
            created_at=datetime.strptime(doc.date, '%Y%m%d')
        ).save()

