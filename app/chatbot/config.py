import os
from dotenv import load_dotenv
from app.database import ENV_PATH

load_dotenv(ENV_PATH)

model = os.getenv("OPENROUTER_MODEL","openrouter:tencent/hy3:free")