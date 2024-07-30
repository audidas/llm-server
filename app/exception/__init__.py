from http import HTTPStatus
from typing import Optional

from fastapi import HTTPException


class LLMException(HTTPException):

    def __init__(
            self,
            status_code: int,
            detail: Optional[str] = None
    ):
        self.status_code = status_code
        self.detail = (detail
                       if (detail is not None)
                       else HTTPStatus(status_code).name)

    def __call__(self, detail: str, status_code: Optional[int] = None):
        self.detail = detail
        if status_code:
            self.status_code = status_code

        return self


NOT_FOUND_EXCEPTION = LLMException(404)
ALREADY_EXIST_EXCEPTION = LLMException(409)
INVALID_REQUEST_EXCEPTION = LLMException(422)
