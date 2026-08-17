from fastapi import FastAPI
from app.routes import rules, webhook

app = FastAPI()
app.include_router(rules.router)
app.include_router(webhook.router)


@app.get("/")
async def health():
    return {"status": "ok"}