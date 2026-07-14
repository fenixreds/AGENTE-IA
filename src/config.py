import os
from dotenv import load_dotenv

load_dotenv()

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "cohere")
MODEL_NAME = os.getenv("MODEL_NAME", "command-a-03-2025")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embed-v4.0")
DOCUMENT_PATH = os.getenv("DOCUMENT_PATH", "data/documento.pdf")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", "db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documentos_rag")