from uuid import UUID

from beanie import PydanticObjectId
from beanie.odm.custom_types.bson.binary import BsonBinary
from pydantic import UUID4

from app.database import Message, Conversation, Documents
from app.view.conversation.schema.response import (
    PreviewElement,
    MessageIncludeDocs,
    ConversationDocuments,
)
from app.view.message.schema.response import MessageConversationWriter


def context_by_conversation_id(conversation_id: UUID4):
    return Message.find({"conversation_id": conversation_id}).sort(+Message.created_at).to_list()


def query_conversation_preview(user_id: str):
    return (
        Conversation.find({"user_id": PydanticObjectId(user_id), "deprecated": False})
        .aggregate(
            [
                {
                    "$lookup": {
                        "from": "Message",
                        "localField": "_id",
                        "foreignField": "conversation_id",
                        "as": "messages",
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "mode": 1,
                        "lastMessage": {"$arrayElemAt": ["$messages", 1]},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "conversation_id": "$_id",
                        "mode": "$mode",
                        "message_id": "$lastMessage._id",
                        "last_content": "$lastMessage.content",
                        "last_timestamp": "$lastMessage.created_at",
                    }
                },
                {"$sort": {"last_timestamp": -1}},
            ],
            projection_model=PreviewElement,
        )
        .to_list()
    )


def query_message_conversation_writer(message_id: UUID4):
    return (
        Message.find(Message.id == message_id)
        .aggregate(
            [
                {
                    "$lookup": {
                        "from": "Conversation",
                        "localField": "conversation_id",
                        "foreignField": "_id",
                        "as": "conversation",
                    }
                },
                {
                    "$project": {
                        "role": "$role",
                        "conversation": {"$arrayElemAt": ["$conversation", -1]},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "role": "$role",
                        "message_id": "$_id",
                        "user_id": "$conversation.user_id",
                        "conversation_id": "$conversation._id",
                    }
                },
            ],
            projection_model=MessageConversationWriter,
        )
        .to_list(length=1)
    )


def query_user_context(conversation_id: UUID4):
    return (
        Message.find({"conversation_id": conversation_id})
        .aggregate(
            [
                {
                    "$lookup": {
                        "from": "Documents",
                        "localField": "_id",
                        "foreignField": "message_id",
                        "as": "documents",
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "message_id": "$_id",
                        "message": {
                            "role": "$role",
                            "content": "$content",
                            "parent_id": "$parent_id",
                            "children": "$children",
                        },
                        "feedback": "$feedback",
                        "created_at": "$created_at",
                        "documents": "$documents",
                    }
                },
            ],
            projection_model=MessageIncludeDocs,
        )
        .to_list()
    )


async def query_conversation_documents(conversation_id: UUID4):
    return (
        await Documents.find()
        .aggregate(
            [
                {
                    "$lookup": {
                        "from": "Message",
                        "localField": "message_id",
                        "foreignField": "_id",
                        "as": "message",
                    }
                },
                {
                    "$project": {
                        "conversation_id": {"$arrayElemAt": ["$message.conversation_id", 0]},
                        "message_created_at": {"$arrayElemAt": ["$message.created_at", 0]},
                        "message_id": "$message_id",
                        "document_id": "$_id",
                        "created_at": "$created_at",
                        "deprecated": "$deprecated",
                        "url": "$url",
                        "title": "$title",
                        "content": "$content",
                    }
                },
                {"$match": {"conversation_id": BsonBinary.from_uuid(conversation_id)}},
                {"$sort": {"message_created_at": 1}},
                {
                    "$project": {
                        "_id": 0,
                        "message_id": "$message_id",
                        "document_id": "$_id",
                        "created_at": "$created_at",
                        "deprecated": "$deprecated",
                        "url": "$url",
                        "title": "$title",
                        "content": "$content",
                    }
                },
            ],
            projection_model=ConversationDocuments,
        )
        .to_list()
    )
