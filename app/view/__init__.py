from fastapi import FastAPI

from app.view.command.api import command_router
from app.view.message.api import message_router
from app.view.user.api import user_router
from app.view.documents.api import document_router
from app.view.conversation.api import conversation_router
from app.view.conversation.chat_api import chat_router
from app.view.conversation.chat_socket import socket_router, knowledge_socket_router


def include_router(app: FastAPI):
    app.include_router(user_router)
    app.include_router(message_router)
    app.include_router(document_router)
    app.include_router(conversation_router)
    app.include_router(chat_router)
    app.include_router(command_router)
    app.include_router(socket_router)
    app.include_router(knowledge_socket_router)
