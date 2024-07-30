from fastapi import Depends

from app.core.service.chat.dto.input import MapChat
from app.database import Conversation, Message
from app.database.model.context import Context
from app.exception import NOT_FOUND_EXCEPTION
from app.view.conversation.sub_function import Generator, generator_mapper
from .abc import ChatUseCae


class MapChatUseCase(ChatUseCae):

    def __init__(self, generators: dict = Depends(generator_mapper())):
        self.generator: Generator = generators.get("map")

    async def chat(self, dto: MapChat):
        conversation = await Conversation.find_one(Conversation.id == dto.conversation_id)

        if (conversation is None) or (conversation.user_id_str != dto.user_id):
            raise NOT_FOUND_EXCEPTION("CONVERSATION_NOT_FOUND")

        context = Context(message_id=dto.message_id, context=dto.context)

        await context.save()

        await self.generator.generate(
            model=dto.model,
            conversation_id=conversation.id,
            parent_id=dto.message_id,
            root_id=dto.parent_id,
            websocket=dto.websocket,
        )

    async def first_chat(self, dto):
        conversation = Conversation(user_id=dto.user_id, mode="map")
        root_message = Message(
            id=dto.root_id,
            role="assistant",
            content=str(),
            conversation_id=conversation.id,
            parent_id=None,
            children=[dto.message_id],
        )
        parent_message = Message(
            role="user",
            id=dto.message_id,
            content=dto.content,
            conversation_id=conversation.id,
            parent_id=dto.root_id,
        )

        context = Context(
            message_id=parent_message.id, image_path=dto.image_path, geometry=dto.geometry
        )

        await context.save()
        await conversation.save()
        await root_message.save()
        await parent_message.save()

        async_generator = self.generator.first_generate(
            conversation_id=conversation.id, parent_id=parent_message.id, root_id=root_message.id
        )

        async for stream in async_generator:
            yield stream
