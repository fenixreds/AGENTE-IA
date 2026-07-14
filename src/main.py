import os
from dotenv import load_dotenv

from src.config import DOCUMENT_PATH, VECTOR_DB_DIR
from src.loader import load_and_split_documents
from src.embeddings import build_vectorstore, load_vectorstore
from src.rag_chain import build_qa_chain

load_dotenv()


def ensure_vectorstore():
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        print("Cargando base vectorial existente...")
        return load_vectorstore(VECTOR_DB_DIR)

    print("No existe base vectorial. Procesando documento...")
    chunks = load_and_split_documents(DOCUMENT_PATH)
    print(f"Chunks generados: {len(chunks)}")

    vectorstore = build_vectorstore(chunks, VECTOR_DB_DIR)
    print("Base vectorial creada correctamente.")
    return vectorstore


def main():
    print("Iniciando agente RAG con Cohere...")
    print(f"Documento: {DOCUMENT_PATH}")
    print(f"Directorio vectorial: {VECTOR_DB_DIR}")

    vectorstore = ensure_vectorstore()
    qa_chain = build_qa_chain(vectorstore)

    print("\nAgente listo. Escribe tu pregunta o 'salir' para terminar.\n")

    while True:
        question = input("Pregunta: ").strip()

        if question.lower() in {"salir", "exit", "quit"}:
            print("Cerrando agente.")
            break

        if not question:
            print("Escribe una pregunta válida.\n")
            continue

        try:
            response = qa_chain.invoke({"query": question})
            answer = response.get("result", "No se obtuvo respuesta.")
            sources = response.get("source_documents", [])

            print("\nRespuesta:")
            print(answer)

            if sources:
                print("\nFuentes recuperadas:")
                for i, doc in enumerate(sources, start=1):
                    page = doc.metadata.get("page", "N/A")
                    source = doc.metadata.get("source", DOCUMENT_PATH)
                    fragment = doc.page_content[:200].replace("\n", " ")
                    print(f"{i}. Página: {page} | Fuente: {source}")
                    print(f"   Fragmento: {fragment}...")
            else:
                print("\nNo se devolvieron fuentes.")

            print("\n" + "-" * 80 + "\n")

        except Exception as e:
            print(f"\nOcurrió un error: {e}\n")


if __name__ == "__main__":
    main()