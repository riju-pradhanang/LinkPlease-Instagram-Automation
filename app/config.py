import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:devpass@localhost:5432/linkplease",
)
PSEUDOGRAM_API_KEY = os.environ["PSEUDOGRAM_API_KEY"]
PSEUDOGRAM_BASE_URL = "https://pseudogram-api.onrender.com"