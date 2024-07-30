from typing import Union, Optional

import redis as redis_client
from beanie import PydanticObjectId
from pydantic import UUID4

from app.config import RedisConfig, JWTConfig

__RedisClient = redis_client.StrictRedis(
    host=RedisConfig.HOST,
    port=RedisConfig.PORT,
    password=RedisConfig.PASSWORD,
    db=0
)


def set_document_pre_link(
        document_id: UUID4,
        document_url: str
):
    __RedisClient.setex(
        name=str(document_id),
        value=document_url,
        time=3600
    )


def set_refresh_token_ex(
        uid: Union[PydanticObjectId, str],
        value: str
):
    uid = str(uid)

    __RedisClient.setex(
        name=uid,
        value=value,
        time=JWTConfig.REFRESH_EXPIRED_AT
    )


def get_refresh_token(uid) -> Optional[str]:
    token: bytes = __RedisClient.get(uid)

    return (
        token.decode('utf-8')
        if token is not None
        else None
    )


def delete_refresh_token(uid):

    __RedisClient.delete(str(uid))
