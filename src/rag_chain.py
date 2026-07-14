from langchain_cohere import ChatCohere
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from src.config import MODEL_NAME

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
Eres un asistente de preguntas y respuestas basado únicamente en documentos recuperados.

Tu tarea es responder la PREGUNTA usando solo la información del CONTEXTO.

Reglas obligatorias:
1. Usa únicamente la información del CONTEXTO.
2. No uses conocimiento externo, aunque conozcas la respuesta.
3. Si la respuesta no aparece de forma clara en el CONTEXTO, responde exactamente:
   "No lo sé según el documento."
4. No inventes nombres, fechas, cifras, definiciones ni explicaciones.
5. Si el CONTEXTO es parcial o ambiguo, indícalo brevemente.
6. Responde de forma breve, precisa y literal al contenido recuperado.
7. Si varias partes del CONTEXTO se contradicen, menciona la contradicción y no elijas una versión sin decirlo.

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA:
"""
)

def get_llm():
    return ChatCohere(
        model=MODEL_NAME,
        temperature=0
    )

def build_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    return RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )