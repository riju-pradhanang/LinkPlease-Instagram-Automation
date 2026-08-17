from fastapi import FastAPI
from app.config import settings
from app.db import engine, Base
from app.routes import rules, webhook, stats

# Initialize Database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# Register routers
app.include_router(rules.router)
app.include_router(webhook.router)
app.include_router(stats.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to linkplease IG Automation API", "status": "running"}
