import os

PORT = int(os.environ.get("PORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL")