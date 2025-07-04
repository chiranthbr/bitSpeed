import os

PORT = int(os.environ.get("PORT", 8000))
DATABASE_URL = os.getenv("mysql+pymysql://root:USZmFipoJUtkXCFdwNCarTYRhHJiouyZ@yamabiko.proxy.rlwy.net:28356/railway")