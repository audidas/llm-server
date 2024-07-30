from typing import Type

from .abc import ChatUseCae
from .knowledge_usecase import KnowledgeChatUseCase
from .map_usecase import MapChatUseCase


class ChatService:
    map_chat: Type[ChatUseCae] = MapChatUseCase
    map_first_chat: Type[ChatUseCae] = MapChatUseCase

    knowledge_chat: Type[ChatUseCae] = KnowledgeChatUseCase
    knowledge_first_chat: Type[ChatUseCae] = KnowledgeChatUseCase
