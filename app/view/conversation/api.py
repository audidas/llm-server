from datetime import datetime
from http import HTTPStatus
from typing import Union

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends
from pydantic import UUID4

from app.database import Conversation, Message, Command
from app.database.query import query_conversation_preview, query_user_context
from app.exception import NOT_FOUND_EXCEPTION
from app.security.auth import authorization
from app.view.conversation.schema.response import ContextResponse, MessageIncludeDocs, MapContextResponse

conversation_router = APIRouter()


@conversation_router.get(
    path="/conversations",
    summary="기존 대화 내역 미리보기(리스트)",
    tags=["Conversation"],
    status_code=HTTPStatus.OK,
)
async def conversation_preview(
        user_id: str = Depends(authorization),
):
    return await query_conversation_preview(user_id)


@conversation_router.get(
    path="/conversations/{conversation_id}",
    summary="대화 내역 조회",
    response_model=Union[ContextResponse, MapContextResponse],
    tags=["Conversation"],
)
async def conversation_contest(conversation_id: UUID4, user_id: str = Depends(authorization)):
    conversation = await Conversation.find_one(Conversation.id == conversation_id)

    if (conversation is None) or (conversation.user_id_str != user_id):
        raise NOT_FOUND_EXCEPTION("CONVERSATION NOT FOUND")

    message_list: list[MessageIncludeDocs] = await query_user_context(conversation.id)

    return ContextResponse(
        messages=message_list,
        conversation_id=conversation.id,
        user_id=conversation.user_id_str,
        created_at=conversation.created_at,
    )


@conversation_router.delete(
    path="/conversations",
    summary="conversation 일괄 삭제",
    status_code=HTTPStatus.NO_CONTENT,
    tags=["Conversation"],
)
async def deprecate_all_conversation(user_id: str = Depends(authorization)):
    await Conversation.find({"user_id": PydanticObjectId(user_id)}).update_many(
        {"$set": {Conversation.deprecated: True}}
    )


@conversation_router.delete(
    path="/conversations/{conversation_id}",
    summary="conversation 삭제",
    status_code=HTTPStatus.NO_CONTENT,
    tags=["Conversation"],
)
async def deprecated_one_conversation(
        conversation_id: UUID4, user_id: str = Depends(authorization)
):
    conversation = await Conversation.find_one(Conversation.id == conversation_id)

    if (conversation is None) or (conversation.user_id_str != user_id):
        raise NOT_FOUND_EXCEPTION("CONVERSATION_NOT_FOUND")

    conversation.deprecated = True
    await conversation.replace()


@conversation_router.get("/conversations/struct/change")
async def change_struct():
    conversations = await Conversation.find().to_list()

    for i, conversation in enumerate(conversations):

        first_message = Message(
            role="assistant",
            content="",
            conversation_id=conversation.id,
            children=[],
        )

        child_message = (
            await Message.find(Message.conversation_id == conversation.id)
            .sort(+Message.created_at)
            .to_list()
        )

        first_message.children.append(child_message[0].id)

        await first_message.save()

        for i, message in enumerate(child_message):
            if i == 0 & len(child_message) > 1:
                message.parent_id = first_message.id
                message.children.append(child_message[i + 1].id)
                await message.replace()
            elif i == len(child_message) - 1 | i == len(child_message) - 2:
                message.parent_id = child_message[i - 1].id
                await message.replace()
            else:
                message.parent_id = child_message[i - 1].id
                if i + 1 < len(child_message):
                    message.children.append(child_message[i + 1].id)
                await message.replace()

    return {"data": "ok"}


def build_tree(
        messages,
):
    tree = {}
    current_node = None
    previous = datetime(year=1999, month=1, day=1)
    for message in messages:
        message_id = message.message_id

        if message.message.parent_id is None:
            tree["root"] = message.message_id

        if previous < message.created_at:
            previous = message.created_at
            current_node = message.message_id

        tree[message_id] = {
            "id": message_id,
            "message": message.message,
            "documents": message.documents,
            "created_at": message.created_at,
            "parent": message.message.parent_id,
        }

    tree['current_node'] = current_node
    return tree


@conversation_router.get("/conversations/get-struct/{conversation_id}")
async def get_struct(conversation_id: UUID4):
    conversation = await Conversation.find_one(Conversation.id == conversation_id)

    if conversation is None:
        raise NOT_FOUND_EXCEPTION("CONVERSATION_NOT_FOUND")

    message_list = await query_user_context(conversation.id)

    tree = build_tree(message_list)
    return tree
