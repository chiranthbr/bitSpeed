import os
from dotenv import load_dotenv

load_dotenv()
PORT = int(os.environ.get("PORT", 8000))
DATABASE_URL = os.getenv("DATABASE_URL")