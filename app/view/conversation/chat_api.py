from typing import Annotated, Union
from fastapi import APIRouter, Depends, WebSocket, WebSocketException, status
from fastapi.params import Query
from pydantic import UUID4
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

chat_router = APIRouter(prefix="/conversations")


@chat_router.post(
    summary="대화 시작하기 (Map)",
    tags=["Map"],
    path="/map",
)
def map_first_chat(
    request: MapFirstRequest,
    user_id: str = Depends(authorization),
    use_case: ChatUseCae = Depends(ChatService.map_first_chat),
):
    return EventSourceResponse(
        use_case.first_chat(
            MapFirstChat(
                user_id=user_id,
                content=request.content,
                geometry=request.context.geometry,
                image_path=request.context.image_path,
                root_id=request.root_id,
                message_id=request.message_id,
            )
        )
    )


@chat_router.post(summary="대화 시작하기 (Knowledge)", tags=["Knowledge"], path="/knowledge")
async def knowledge_first_chat(
    request: KnowledgeFirstRequest,
    user_id: str = Depends(authorization),
    use_case: ChatUseCae = Depends(ChatService.knowledge_first_chat),
):
    return EventSourceResponse(
        use_case.first_chat(
            KnowledgeFirstChat(
                user_id=user_id,
                content=request.content,
                root_id=request.root_id,
                message_id=request.message_id,
            )
        )
    )


@chat_router.post(summary="대화 이어나가기 (Map)", tags=["Map"], path="/map/{conversation_id}")
def map_chat(
    conversation_id: UUID4,
    request: MapRequest,
    user_id: str = Depends(authorization),
    use_case: ChatUseCae = Depends(ChatService.map_chat),
):
    return EventSourceResponse(
        use_case.chat(
            MapChat(
                user_id=user_id,
                content=request.content,
                geometry=request.context.geometry,
                image_path=request.context.image_path,
                parent_id=request.parent_id,
                message_id=request.message_id,
                conversation_id=conversation_id,
            )
        )
    )


@chat_router.post(
    summary="대화 이어나가기 (Knowledge)", tags=["Knowledge"], path="/knowledge/{conversation_id}"
)
def knowledge_chat(
    conversation_id: UUID4,
    request: KnowledgeRequest,
    user_id: str = Depends(authorization),
    use_case: ChatUseCae = Depends(ChatService.knowledge_chat),
):
    return EventSourceResponse(
        use_case.chat(
            KnowledgeChat(
                user_id=user_id,
                content=request.content,
                parent_id=request.parent_id,
                message_id=request.message_id,
                conversation_id=conversation_id,
            )
        )
    )
