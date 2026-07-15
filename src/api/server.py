import os
import shutil
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import DOCUMENT_PATH, VECTOR_DB_DIR
from src.loader import load_and_split_documents
from src.embeddings import build_vectorstore, load_vectorstore
from src.rag_chain import build_qa_chain

load_dotenv()

app = FastAPI(title="Agente IA - RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_vectorstore():
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        vectorstore = load_vectorstore(VECTOR_DB_DIR)
        try:
            if vectorstore._collection.count() > 0:
                return vectorstore
        except Exception:
            pass

        try:
            shutil.rmtree(VECTOR_DB_DIR)
        except Exception:
            pass

    chunks = load_and_split_documents(DOCUMENT_PATH)
    return build_vectorstore(chunks, VECTOR_DB_DIR)


vectorstore = init_vectorstore()
qa_chain = build_qa_chain(vectorstore)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@app.get("/")
async def home():
    return FileResponse("frontend/templates/index.html")


@app.get("/api/health")
async def health():
    return {"status": "ok", "agent": "RAG Cohere + ChromaDB"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    question = payload.message.strip()

    if not question:
        return ChatResponse(
            answer="Por favor escribe una pregunta válida.",
            sources=[],
        )

    try:
        response = qa_chain.invoke({"query": question})
        answer = response.get("result", "No se obtuvo respuesta.")
        source_documents = response.get("source_documents", [])

        sources = []
        for doc in source_documents:
            sources.append(
                {
                    "page": doc.metadata.get("page", "N/A"),
                    "source": doc.metadata.get("source", DOCUMENT_PATH),
                    "content": doc.page_content[:300],
                }
            )

        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        return ChatResponse(
            answer=f"Error al procesar la pregunta: {str(e)}",
            sources=[],
        )