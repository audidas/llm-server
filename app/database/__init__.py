from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import DatabaseConfig
from app.database.model import User, Conversation, Message, Documents
from app.database.model.command import Command
from app.database.model.context import Context
from app.database.model.prompt import Prompt


async def init_mongodb(db_name: str = DatabaseConfig.NAME):
    client = AsyncIOMotorClient(DatabaseConfig.URL)

    await init_beanie(
        getattr(client, db_name), document_models=[
            User, Message, Conversation, Documents, Prompt, Context, Command
        ]
    )
