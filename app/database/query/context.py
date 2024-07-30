from typing import Dict, List

from pydantic import UUID4

from app.database.query import context_by_conversation_id


async def query_llm_context(conversation_id: UUID4) -> List[Dict]:
    context = await context_by_conversation_id(conversation_id)

    return [{"role": message.role, "content": message.content} for message in context]
