from datetime import datetime

from pydantic import BaseModel


class SignUpResponse(BaseModel):
    name: str
    email: str
    created_at: datetime


class SignInResponse(BaseModel):
    access_token: str
    access_expired_at: datetime

    refresh_token: str
    refresh_expired_at: datetime

class UserMyInformationResponse(BaseModel):
    name: str
    email: str
    created_at: datetime
