from app import create_app
from app.database import init_mongodb

app = create_app()


@app.get("/health-check")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def on_startup():
    await init_mongodb()


if __name__ == "__main__":
    from uvicorn import run

    run(app)
