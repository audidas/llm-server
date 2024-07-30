from fastapi import APIRouter, Depends
from pydantic import UUID4

from app.database import Message
from app.database.query import query_message_conversation_writer
from app.exception import NOT_FOUND_EXCEPTION
from app.security.auth import authorization
from app.view.message.schema.request import FeedbackRequest

message_router = APIRouter()


@message_router.patch('/messages/{message_id}/feedbacks')
async def leaved_feedback(
        message_id: UUID4,
        request: FeedbackRequest,
        user_id: str = Depends(authorization)
):
    message = await query_message_conversation_writer(message_id)
    if (
            len(message) == 0 or
            str(message[0].user_id) != user_id or
            message[0].message_id != message_id
    ):
        raise NOT_FOUND_EXCEPTION("MESSAGE NOT FOUND")

    message = message.pop()

    await Message.find_one(
        Message.id == message.message_id
    ).update(
        {
            "$set": {Message.feedback: request.feedback}
        }
    )
