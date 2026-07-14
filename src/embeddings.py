from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings
from src.config import EMBEDDING_MODEL, VECTOR_DB_DIR, COLLECTION_NAME

def get_embeddings():
    return CohereEmbeddings(model=EMBEDDING_MODEL)

def build_vectorstore(chunks, persist_directory: str = VECTOR_DB_DIR):
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=COLLECTION_NAME
    )

    try:
        vectorstore.persist()
    except Exception:
        pass

    return vectorstore

def load_vectorstore(persist_directory: str = VECTOR_DB_DIR):
    embeddings = get_embeddings()

    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )