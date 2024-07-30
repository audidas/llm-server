from json import dumps, loads
from typing import Optional
from uuid import uuid4, UUID

import requests
from pydantic import UUID4

from app import llm
from app.database import Documents
from app.database import Message
from app.database.query.context import query_llm_context
from app.database.query.document import save_documents_from_prompt
from app.database.query.message import adopt_child_message
from app.database.query.prompt import save_prompt
from app.view.conversation.sub_function.abc import Generator
import json
from websocket import create_connection


class KnowledgeGenerator(Generator):

    def generate(
        self,
        conversation_id: UUID4,
        model: str,
        parent_id: UUID4,
        root_id: Optional[UUID4] = None,
        websocket=None,
        *args,
        **kwargs,
    ):
        return self.__generate(
            is_first_chat=False,
            conversation_id=conversation_id,
            parent_id=parent_id,
            websocket=websocket,
            model=model,
        )

    def first_generate(
        self,
        conversation_id: UUID4,
        parent_id: UUID4,
        root_id: Optional[UUID4] = None,
        *args,
        **kwargs,
    ):
        return self.__generate(
            is_first_chat=True,
            conversation_id=conversation_id,
            parent_id=parent_id,
            model="gpt-3.5-turbo"
        )

    async def __generate(
        self,
        is_first_chat: bool,
        model: str,
        conversation_id: UUID4,
        parent_id: UUID4,
        websocket=None,
    ):
        # Init
        init_message = self.__init_message(conversation_id)
        content, message_id = list(), UUID(init_message["message_id"])

        await websocket.send_json(init_message)
        # request:Request
        context = await query_llm_context(conversation_id)
        # Stream
        ws = create_connection(
            f"ws://10.0.10.102:14003/knowledge/chat/{conversation_id}?message_id={message_id}&model={model}"
        )
        ws.send(json.dumps(context))

        while True:
            result = ws.recv()
            result_json = json.loads(result)
            if result_json["role"] == "documents":
                [
                    await Documents(
                        message_id=message_id,
                        url=document["url"],
                        title=document["title"],
                        content=document["content"],
                        date=document["date"],
                    ).save()
                    for document in result_json["content"]
                ]
            elif result_json["role"] == "done":
                await websocket.send_json(result_json)
                break
            elif result_json["role"] == "assistant":
                result_json["message_id"] = str(message_id)
                content.append(result_json["content"])
                await websocket.send_json(result_json)
            elif result_json["role"] == "status":
                result_json["message_id"] = str(message_id)
                await websocket.send_json(result_json)
        # Exit
        await adopt_child_message(
            parent_id,
            Message(
                id=message_id,
                role="assistant",
                parent_id=parent_id,
                content=str().join(content),
                conversation_id=conversation_id,
                model=model
            ),
        )

    @staticmethod
    def __init_message(conversation_id: UUID4):
        return {
            "role": "assistant",
            "content": str(),
            "message_id": str(uuid4()),
            "conversation_id": str(conversation_id),
        }

    @staticmethod
    def __serialize_message(response: dict, message_id: UUID4):
        for line in response.iter_lines():
            stream = loads(line)
            stream["message_id"] = str(message_id)

            if stream["role"] == "[done]":
                return

            yield stream
