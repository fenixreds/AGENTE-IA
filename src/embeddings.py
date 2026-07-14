from langchain_chroma import Chroma
from langchain_cohere import CohereEmbeddings

EMBEDDING_MODEL = "embed-v4.0"

def get_embeddings():
    return CohereEmbeddings(model=EMBEDDING_MODEL)

def build_vectorstore(chunks, persist_directory: str):
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vectorstore

def load_vectorstore(persist_directory: str):
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )