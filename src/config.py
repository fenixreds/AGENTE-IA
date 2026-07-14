import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "command-a-03-2025")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embed-v4.0")