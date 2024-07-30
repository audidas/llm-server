from fastapi import FastAPI

from app.view import include_router
from app.security.cors import include_cors_middleware


def create_app():
    app = FastAPI()

    include_router(app)
    include_cors_middleware(app)

    return app
