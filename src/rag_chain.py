from langchain_classic.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_community.chat_models import ChatOllama

from src.config import (
    MODEL_PROVIDER,
    MODEL_NAME,
    OPENAI_API_KEY,
    COHERE_API_KEY,
    OLLAMA_BASE_URL,
)

def get_llm():
    if MODEL_PROVIDER == "openai":
        return ChatOpenAI(model=MODEL_NAME, temperature=0, api_key=OPENAI_API_KEY)
    elif MODEL_PROVIDER == "cohere":
        return ChatCohere(model=MODEL_NAME, temperature=0, cohere_api_key=COHERE_API_KEY)
    elif MODEL_PROVIDER == "ollama":
        return ChatOllama(model=MODEL_NAME, temperature=0, base_url=OLLAMA_BASE_URL)
    else:
        raise ValueError(f"Proveedor no soportado: {MODEL_PROVIDER}")

def build_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = get_llm()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )