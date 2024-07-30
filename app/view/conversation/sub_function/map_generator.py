from json import dumps, JSONDecodeError
import json
from typing import Optional
from uuid import uuid4, UUID

from pydantic import UUID4

from app.database import Message
from app.database.model.command import Command
from app.database.model.context import Context
from app.database.query.context import query_llm_context
from app.database.query.message import adopt_child_message
from app.llm import map_message
from app.view.conversation.sub_function import Generator
from websocket import create_connection


class MapGenerator(Generator):

    def first_generate(
            self, conversation_id: UUID4, parent_id: UUID4, root_id: Optional[UUID4] = None, **kwargs
    ):
        return self.__generate(
            conversation_id=conversation_id,
            parent_id=parent_id,
        )

    def generate(
            self,
            conversation_id: UUID4,
            parent_id: UUID4,
            model: str,
            root_id: Optional[UUID4] = None,
            websocket=None,
            *args,
            **kwargs,
    ):
        return self.__generate(
            model=model,
            conversation_id=conversation_id,
            parent_id=parent_id,
            websocket=websocket,
        )

    async def __generate(
            self,
            model: str,
            conversation_id: UUID4,
            parent_id: UUID4,
            websocket=None,
    ):
        # Init
        init_message = self.__init_message(conversation_id)
        message_id = UUID(init_message["message_id"])

        await websocket.send_json(init_message)

        # Prompt
        context = await Context.query_by_message_id(parent_id)
        messages = await query_llm_context(conversation_id=conversation_id)

        print('1. LLM WEBSOCKET OPEN')
        ws = create_connection(
            f"ws://10.0.10.102:14003/map/chat/{conversation_id}?message_id={message_id}&model={model}"
        )
        data = json.dumps({"messages": messages, "context": context})
        print('2. SEND JSON')
        ws.send(data)
        print('3. SEND JSON SUCCESS')
        content = ""

        print('4. START WHILE LOOP')
        while True:
            result = ws.recv()
            try:
                result = json.loads(result)
            except JSONDecodeError:
                print(result)
                raise IndexError

            print('5. RECEIVE SUCCESS')

            if result.get("role") == "error":

                await websocket.send_json(result)

            elif result.get("role") == "commands":
                commands = result.get("content")

                await Command(message_id=message_id, commands=commands).save()
                await websocket.send_json(result)

                print('5-1. COMMAND ROLE HANDLE')

            elif result.get("role") == "done":
                await websocket.send_json(result)
                print('6. DONE HANDLE')
                break
            elif result.get("role") == "assistant":
                result["message_id"] = str(message_id)

                content += result.get("content")
                print('7. HANDLE ASSISTANT')
                await websocket.send_json(
                    {
                        "message_id": str(message_id),
                        "content": result.get("content"),
                    }
                )
                print('7 - 1. SEND ASSISTANT')
            elif result.get("role") == "status":

                await websocket.send_json(result)
                print('8 - STATUS SEND')

        await adopt_child_message(
            parent_id,
            Message(
                model=model,
                id=message_id,
                role="assistant",
                content=content,
                conversation_id=conversation_id,
                parent_id=parent_id,
            ),
        )

    @staticmethod
    def __init_message(conversation_id: UUID4):
        return {
            "role": "assistant",
            "content": str(),
            "conversation_id": str(conversation_id),
            "message_id": str(uuid4()),
        }
