from http import HTTPStatus
from typing import Union

from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Header

from app.config import JWTConfig
from app.database.memory import set_refresh_token_ex, get_refresh_token, delete_refresh_token
from app.database.model import User
from app.security.auth import authorization, oauth2_scheme
from app.security.jwt_token import Encoder, Decoder
from app.security.password import hash_password, verify_password
from app.view.user.schema.request import SignUpRequest, SignInRequest, ChangePasswordRequest
from app.view.user.schema.response import SignInResponse, SignUpResponse, UserMyInformationResponse
from app.exception import (ALREADY_EXIST_EXCEPTION,
                           NOT_FOUND_EXCEPTION,
                           INVALID_REQUEST_EXCEPTION)

user_router = APIRouter()


@user_router.post(
    path='/users/sign-up',
    summary="회원가입",
    tags=["User"],
    response_model=SignUpResponse,
    status_code=HTTPStatus.CREATED
)
async def user_sign_up(request: SignUpRequest):
    if await User.find_one({"email": request.email}):
        raise ALREADY_EXIST_EXCEPTION("USER_ALREADY_EXIST")

    request.password = hash_password(request.password)

    user = User.validate(request.model_dump()).save()

    return await user


@user_router.post(
    path='/users/sign-in',
    summary="로그인",
    tags=["User"],
    response_model=SignInResponse,
    status_code=HTTPStatus.OK
)
async def user_sign_in(request: SignInRequest):
    user = await User.find_one({"email": request.email})

    if user is None:
        raise NOT_FOUND_EXCEPTION("USER_NOT_FOUND")

    if not verify_password(request.password, user.password):
        raise INVALID_REQUEST_EXCEPTION("INVALID PASSWORD")

    access_token, access_expired_at = Encoder.access_token(user.id_str)
    refresh_token, refresh_expired_at = Encoder.refresh_token(user.id_str)

    set_refresh_token_ex(
        uid=user.id_str,
        value=refresh_token
    )

    return SignInResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expired_at=access_expired_at,
        refresh_expired_at=refresh_expired_at
    )


@user_router.put(
    path='/users/tokens',
    summary="토큰 재발급",
    tags=["User"],
)
async def user_token_refresh(
        refresh_token: str = Header(...)
):
    payload = Decoder.refresh_token(refresh_token)

    if payload["typ"] != JWTConfig.REFRESH:
        raise INVALID_REQUEST_EXCEPTION("INVALID_REFRESH_TOKEN_ARRIVED")

    saved_token = get_refresh_token(payload.get("sub"))
    if refresh_token != saved_token:
        raise NOT_FOUND_EXCEPTION("TOKEN_ALREADY_EXPIRED")

    user = await User.find_one(User.id == payload['sub'])
    if user is None:
        raise NOT_FOUND_EXCEPTION("USER_NOT_FOUND")

    new_access_token, new_access_expired_at = Encoder.access_token(payload.get('sub'))
    new_refresh_token, new_refresh_expired_at = Encoder.refresh_token(payload.get('sub'))

    set_refresh_token_ex(payload['sub'], new_refresh_token)

    return SignInResponse(
        access_token=new_access_token,
        access_expired_at=new_access_expired_at,
        refresh_token=new_refresh_token,
        refresh_expired_at=new_refresh_expired_at
    )


@user_router.get(
    path='/users/me',
    summary="내 정보 조회",
    tags=["User"],
    response_model=UserMyInformationResponse
)
async def query_my_information(
        user_id: str = Depends(authorization)
):
    user = await User.find_one(User.id == PydanticObjectId(user_id))

    if user is None or user.id_str != user_id:
        raise NOT_FOUND_EXCEPTION("USER_NOT_FOUND")

    return user


@user_router.delete(
    path='/users/sign-out',
    summary="로그아웃",
    tags=["User"],
    status_code=HTTPStatus.NO_CONTENT
)
async def user_sign_out(
        user_id: str = Depends(authorization)
):
    delete_refresh_token(user_id)


@user_router.patch(
    path='/users/passwords',
    summary='비밀번호 변경',
    tags=['User'],
    status_code=HTTPStatus.NO_CONTENT
)
async def update_password(
        request: ChangePasswordRequest,
        user_id: str = Depends(authorization)
):
    user = await User.find_one(User.id == PydanticObjectId(user_id))

    if user is None or user.id_str != user_id:
        raise NOT_FOUND_EXCEPTION("USER_NOT_FOUND")

    if not verify_password(request.old_password, user.password):
        raise INVALID_REQUEST_EXCEPTION("INVALID_PASSWORD_ARRIVED")

    user.password = hash_password(request.new_password)
    await user.replace()
