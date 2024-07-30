from typing import List

from fastapi import APIRouter, Depends, Request
from pydantic import UUID4

from app.database import Command, Message
from app.database.query import context_by_conversation_id
from app.exception import NOT_FOUND_EXCEPTION
from app.security.auth import authorization

command_router = APIRouter()


@command_router.get(
    summary="Message에 맞는 Commands 조회",
    tags=["Command"],
    path="/commands/{message_id}",
)
async def get_command_by_conversation_id(message_id: UUID4, user_id: str = Depends(authorization)):
    commands = await Command.find_one(Command.message_id == message_id)

    if commands is None:
        raise NOT_FOUND_EXCEPTION("COMMAND NOT FOUND")

    return {"commands": commands.commands}


@command_router.post(
    summary="Command 등록 (for LLM Server)",
    tags=["Command"],
    path="/commands",
)
async def create_command(command_data: Request):
    data = await command_data.json()
    message_id = data.get("message_id")
    commands = data.get("commands")

    await Command(message_id=message_id, commands=commands).save()


@command_router.get(path="/commands/conversations/{conversation_id}")
async def get_last_commands(conversation_id: UUID4, user_id: str = Depends(authorization)):
    context: List[Message] = await context_by_conversation_id(conversation_id)

    last_commands = {}

    for message in context:
        command: Command = await Command.find_one(Command.message_id == message.id)

        if command is None:
            continue

        for cmd in command.commands:
            func = cmd.get("func")
            last_commands[func] = cmd

    return {"commands": list(last_commands.values())}
