from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from beanie import BeanieObjectId

from app.security.jwt_token import Decoder

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/sign-in")


def authorization(jwt_token: str = Depends(oauth2_scheme)):
    payload = Decoder.access_token(jwt_token)

    return payload["sub"]
