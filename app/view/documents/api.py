from http import HTTPStatus

import boto3
from fastapi import APIRouter
from pydantic import UUID4

from app.config import S3Config
from app.database import Documents
from app.database.query import query_conversation_documents
from app.exception import NOT_FOUND_EXCEPTION
from app.view.documents.schema.request import CreateDocumentRequest
from app.view.documents.schema.response import (
    document_res_adapter,
    DocumentListResponse,
    DocumentElement,
)
from app.view.documents.sub_function import create_pre_signed_url

document_router = APIRouter()


@document_router.post(
    path="/messages/{message_id}/documents",
    summary="Document 생성 (for LLM Server)",
    tags=["Document"],
)
async def create_document(message_id: UUID4, request: CreateDocumentRequest):
    [
        await Documents(
            message_id=message_id,
            url=document.url,
            title=document.title,
            content=document.content,
            date=document.date,
        ).save()
        for document in request.document_list
    ]

    return {"message": "Document 생성 완료"}


@document_router.get(
    path="/documents/{document_id}", summary="Document 단일 조회", tags=["Document"]
)
async def view_documentation(document_id: UUID4):
    document = await Documents.find_one(Documents.id == document_id)

    if document.url.startswith("http"):
        document_url = document.url

    else:
        path, page = document.url.split("#")
        document_url = create_pre_signed_url(path) + "#" + page

    return {"document_url": document_url}


@document_router.get(
    path="/conversations/{conversation_id}/documents",
    summary="Conversation의 Document 리스트",
    tags=["Document"],
)
async def conversation_document_list(
    conversation_id: UUID4,
):
    return await query_conversation_documents(conversation_id)


@document_router.get(
    path="/messages/{message_id}/documents",
    summary="Document 조회",
    tags=["Document"],
)
async def query_document(
    message_id: UUID4,
):
    document_list = await Documents.find(
        {
            Documents.message_id: message_id,
        }
    ).to_list()

    return document_res_adapter.validate_python(document_list, from_attributes=True)


@document_router.delete(
    path="/documents/{document_id}",
    summary="Document 삭제",
    tags=["Document"],
    status_code=HTTPStatus.NO_CONTENT,
)
async def deprecate_document(document_id: UUID4):
    document = await Documents.find_one(Documents.id == document_id)
    if document is None:
        raise NOT_FOUND_EXCEPTION("DOCUMENT NOT FOUND")

    document.deprecated = True
    await document.replace()
