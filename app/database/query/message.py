from pydantic import UUID4

from app.database import Message


async def adopt_child_message(
        parent_id: UUID4, child_message: Message
):
    parent_message = await Message.find_one(Message.id == parent_id)

    await child_message.save()
    await parent_message.append_children(child_message)
