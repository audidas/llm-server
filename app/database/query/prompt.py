from pydantic import ValidationError

from app.database.model.prompt import message_adapter, documents_adapter, Prompt
from app.exception import INVALID_REQUEST_EXCEPTION


async def save_prompt(prompt_json, message_id) -> Prompt:
    try:
        messages = message_adapter.validate_python(prompt_json["messages"])
        documents = documents_adapter.validate_python(prompt_json["documents"])

    except ValidationError:
        raise INVALID_REQUEST_EXCEPTION(detail="WRONG_PROMPT_ARRIVED")

    prompt = Prompt(message_id=message_id, messages=messages, documents=documents)
    return await prompt.save()
