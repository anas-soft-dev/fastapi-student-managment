from dotenv import load_dotenv
load_dotenv()
import os

model = os.getenv("OPENROUTER_MODEL","openrouter:tencent/hy3:free")