import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import rules, webhook
from app.services.sender import send_worker_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(send_worker_loop())
    yield
    worker_task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(rules.router)
app.include_router(webhook.router)


@app.get("/")
async def health():
    return {"status": "ok"}