from fastapi import Depends

from app.database import Conversation, Message
from app.exception import NOT_FOUND_EXCEPTION
from app.view.conversation.sub_function import Generator, generator_mapper
from .abc import ChatUseCae
from .dto.input import KnowledgeChat, KnowledgeFirstChat


class KnowledgeChatUseCase(ChatUseCae):

    def __init__(self, generators: dict = Depends(generator_mapper())):
        self.generator: Generator = generators["knowledge"]

    async def chat(self, dto: KnowledgeChat):
        conversation = await Conversation.find_one(Conversation.id == dto.conversation_id)

        if (conversation is None) or (conversation.user_id_str != dto.user_id):
            raise NOT_FOUND_EXCEPTION("CONVERSATION_NOT_FOUND")

        await self.generator.generate(
            conversation_id=conversation.id,
            parent_id=dto.message_id,
            root_id=dto.parent_id,
            websocket=dto.websocket,
            model=dto.model
        )

    async def first_chat(self, dto: KnowledgeFirstChat):
        conversation = Conversation(user_id=dto.user_id, mode="knowledge")
        root_message = Message(
            id=dto.root_id,
            role="assistant",
            content=str(),
            conversation_id=conversation.id,
            parent_id=None,
            children=[dto.message_id],
        )
        message = Message(
            role="user",
            content=dto.content,
            conversation_id=conversation.id,
            parent_id=dto.root_id,
            id=dto.message_id,
        )

        await conversation.save()
        await root_message.save()
        await message.save()

        async_generator = self.generator.first_generate(
            conversation_id=conversation.id, parent_id=message.id, root_id=dto.root_id
        )

        async for stream in async_generator:
            yield stream
