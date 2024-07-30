from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException
from jwt import encode, decode
from jwt.exceptions import (
    ExpiredSignatureError, InvalidAlgorithmError, InvalidSignatureError, InvalidKeyError
)

from app.config import JWTConfig
from app.util import kst_now


class Encoder:

    @staticmethod
    def __generate_token(user_id: str, token_type: str, key: str, expire_sec: int) -> Union[str, datetime]:
        kst = kst_now()
        remain = timedelta(seconds=expire_sec)

        expire = kst + remain
        expired_at = expire.timestamp()


        token = encode(
            payload={
                "sub": user_id,
                "typ": token_type,
                "exp": expired_at,
            },
            key=key,
            algorithm=JWTConfig.ALGORITHM,
        )

        return token, expired_at

    @staticmethod
    def access_token(user_id: str) -> Union[str, datetime]:
        jwt_type = JWTConfig.ACCESS
        key = JWTConfig.ACCESS_KEY
        expire_sec = int(JWTConfig.ACCESS_EXPIRED_AT)

        return Encoder.__generate_token(user_id, jwt_type, key, expire_sec)

    @staticmethod
    def refresh_token(user_id: str) -> Union[str, datetime]:
        jwt_type = JWTConfig.REFRESH
        key = JWTConfig.REFRESH_KEY
        expire_sec = int(JWTConfig.REFRESH_EXPIRED_AT)

        return Encoder.__generate_token(user_id, jwt_type, key, expire_sec)


class Decoder:

    @staticmethod
    def __decode_token(token, key):
        try:
            return decode(
                jwt=token,
                key=key,
                algorithms=JWTConfig.ALGORITHM
            )
        except ExpiredSignatureError:
            raise HTTPException(401, "EXPIRED_TOKEN_ARRIVED")
        except (
                InvalidAlgorithmError,
                InvalidSignatureError,
                InvalidKeyError
        ):
            raise HTTPException(500, "YOU_SHELL_NOT_PASS!")

    @staticmethod
    def access_token(token):
        key = JWTConfig.ACCESS_KEY

        return Decoder.__decode_token(token, key)

    @staticmethod
    def refresh_token(token):
        key = JWTConfig.REFRESH_KEY

        return Decoder.__decode_token(token, key)
