from langchain_cohere import ChatCohere
from langchain_classic.chains import RetrievalQA
from src.config import MODEL_NAME


def get_llm():
    return ChatCohere(
        model=MODEL_NAME,
        temperature=0
    )

def build_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    qa_chain = RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain