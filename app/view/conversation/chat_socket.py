import json
import enum
from typing import Annotated, Union
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, WebSocketException, status
from fastapi.params import Query
from pydantic import UUID4
from app.database import Conversation, Message
from sse_starlette import EventSourceResponse
from app.security.jwt_token import Decoder

from app.core.service.chat.dto.input import KnowledgeFirstChat, KnowledgeChat, MapChat, MapFirstChat
from app.security.auth import authorization
from app.view.conversation.schema.request import (
    KnowledgeFirstRequest,
    KnowledgeRequest,
    MapFirstRequest,
    MapRequest,
)

from app.core.service.chat import ChatUseCae, ChatService
from uuid import UUID

socket_router = APIRouter()
knowledge_socket_router = APIRouter()


class Model(str, enum.Enum):
    gpt = "gpt-3.5-turbo"
    llama = "SatCHAT-llama-3-38-Instruct"
    orion = "SatCHAT-Orion-14B-Chat"


async def get_user(
        websocket: WebSocket,
        token: Annotated[Union[str, None], Query()] = None,
):
    if token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    payload = Decoder.access_token(token)
    return payload["sub"]


@socket_router.websocket("/knowledge/{conversation_id}")
async def knowledge_chat_ws(
        conversation_id: UUID4,
        websocket: WebSocket,
        model: Model = Model.gpt,
        user_id: str = Depends(get_user),
        use_case: ChatUseCae = Depends(ChatService.knowledge_chat),
):
    conversation = await Conversation.find_one(Conversation.id == conversation_id)
    if conversation is None:
        conversation = Conversation(id=conversation_id, user_id=user_id, mode="knowledge")

        await conversation.save()

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            content = data.get("content")
            parent_id = data.get("parent_id")
            message_id = data.get("message_id")
            root_id = data.get("root_id")
            if root_id != "" and root_id != None:
                root_meesage = Message(
                    id=root_id,
                    role="assistant",
                    content=str(),
                    conversation_id=str(conversation.id),
                    parent_id=None,
                    children=[message_id],
                )
                message = Message(
                    role="user",
                    content=content,
                    conversation_id=str(conversation.id),
                    parent_id=root_id,
                    id=message_id,
                )
                parent_id = root_id
                await root_meesage.save()
                await message.save()
            else:
                parent_message = await Message.find_one(Message.id == UUID(parent_id))
                if parent_message is None:
                    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
                message = Message(
                    id=message_id,
                    role="user",
                    content=content,
                    conversation_id=str(conversation.id),
                    parent_id=parent_id,
                )
                await message.save()
                await parent_message.append_children(message)
            await use_case.chat(
                KnowledgeChat(
                    user_id=user_id,
                    model=model.value,
                    content=content,
                    conversation_id=conversation.id,
                    parent_id=parent_id,
                    message_id=message_id,
                    websocket=websocket,
                )
            )

    except WebSocketDisconnect:
        print("Front knowledge Disconnect Websocket")
        # await websocket.close()


@socket_router.websocket("/map/{conversation_id}")
async def map_chat_ws(
        conversation_id: UUID4,
        websocket: WebSocket,
        model: Model = Model.gpt,
        user_id: str = Depends(get_user),
        use_case: ChatUseCae = Depends(ChatService.map_chat),
):
    conversation = await Conversation.find_one(Conversation.id == conversation_id)
    if conversation is None:
        conversation = Conversation(id=conversation_id, user_id=user_id, mode="map")

        await conversation.save()

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            content = data.get("content")
            parent_id = data.get("parent_id")
            message_id = data.get("message_id")
            root_id = data.get("root_id")
            context = data.get("context")

            if root_id != "" and root_id != None:
                root_meesage = Message(
                    id=root_id,
                    role="assistant",
                    content=str(),
                    conversation_id=str(conversation.id),
                    parent_id=None,
                    children=[message_id],
                )
                message = Message(
                    role="user",
                    content=content,
                    conversation_id=str(conversation.id),
                    parent_id=root_id,
                    id=message_id,
                )
                parent_id = root_id
                await root_meesage.save()
                await message.save()
            else:
                parent_message = await Message.find_one(Message.id == UUID(parent_id))
                if parent_message is None:
                    raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
                message = Message(
                    id=message_id,
                    role="user",
                    content=content,
                    conversation_id=str(conversation.id),
                    parent_id=parent_id,
                )
                await message.save()
                await parent_message.append_children(message)
            await use_case.chat(
                MapChat(
                    model=model.value,
                    user_id=user_id,
                    content=content,
                    conversation_id=conversation.id,
                    parent_id=parent_id,
                    message_id=message_id,
                    websocket=websocket,
                    context=context,
                )
            )

    except WebSocketDisconnect as e:
        print("Map Front Disconnect WebSocket")

        # await websocket.close()
