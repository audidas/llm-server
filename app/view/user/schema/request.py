from datetime import datetime

from pydantic import computed_field, field_validator
from pydantic import BaseModel, PrivateAttr, Field, ValidationInfo

from app.exception import INVALID_REQUEST_EXCEPTION
from app.util import kst_now


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str):
        if not (9 <= len(v) <= 13):
            raise INVALID_REQUEST_EXCEPTION("INVALID_PASSWORD_EXCEPTION")
        return v


class SignUpRequest(BaseModel):
    email: str
    name: str  # = Field(min_length=2, max_length=5)
    password: str

    _created_at: datetime = PrivateAttr(default_factory=kst_now)

    @computed_field(return_type=datetime)
    def created_at(self):
        return self._created_at

    """
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str):
        if not (9 <= len(v) <= 13):
            raise INVALID_REQUEST_EXCEPTION("INVALID_PASSWORD_EXCEPTION")
        return v

    @field_validator('name', 'email')
    @classmethod
    def validate_fields(cls, v: str, info: ValidationInfo):
        if info.field_name == "name":
            if v.isalpha(): return v

            raise INVALID_REQUEST_EXCEPTION("INVALID_NAME_EXPRESSION")

        elif info.field_name == 'email':
            if '@' in v and '.' in v: return v

            raise INVALID_REQUEST_EXCEPTION("INVALID_EMAIL_EXPRESSION")
    """


class SignInRequest(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str):
        if '@' in v and '.' in v: return v

        raise INVALID_REQUEST_EXCEPTION("INVALID_EMAIL_EXPRESSION")

    """
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str):
        if not (9 <= len(v) <= 13):
            raise INVALID_REQUEST_EXCEPTION("INVALID_PASSWORD_EXCEPTION")
        return v
    """
