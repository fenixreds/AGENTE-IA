import os
import shutil
from dotenv import load_dotenv

from src.config import DOCUMENT_PATH, VECTOR_DB_DIR
from src.loader import load_and_split_documents
from src.embeddings import build_vectorstore, load_vectorstore
from src.rag_chain import build_qa_chain

load_dotenv()


def get_collection_count(vectorstore):
    try:
        return vectorstore._collection.count()
    except Exception:
        return -1


def rebuild_vectorstore():
    print("Procesando documento y creando base vectorial...")
    chunks = load_and_split_documents(DOCUMENT_PATH)
    print(f"Chunks generados: {len(chunks)}")

    vectorstore = build_vectorstore(chunks, VECTOR_DB_DIR)
    count = get_collection_count(vectorstore)
    print(f"Registros en Chroma después de crear la base: {count}")

    return vectorstore


def ensure_vectorstore():
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        print("Cargando base vectorial existente...")
        vectorstore = load_vectorstore(VECTOR_DB_DIR)
        count = get_collection_count(vectorstore)

        print(f"Registros detectados en la colección: {count}")

        if count > 0:
            return vectorstore

        print("La base vectorial existe pero está vacía. Se reconstruirá automáticamente.")

        try:
            shutil.rmtree(VECTOR_DB_DIR)
        except Exception as e:
            print(f"No se pudo eliminar la base anterior: {e}")

    return rebuild_vectorstore()


def print_docs(docs, title, max_chars=400):
    print(f"\n{title}")
    print("=" * 100)

    if not docs:
        print("No se encontraron documentos.")
        print("=" * 100)
        return

    print(f"Cantidad de documentos: {len(docs)}\n")

    for i, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page", "N/A")
        source = doc.metadata.get("source", DOCUMENT_PATH)
        content = doc.page_content[:max_chars].replace("\n", " ")

        print(f"Documento #{i}")
        print(f"Página: {page}")
        print(f"Fuente: {source}")
        print(f"Contenido: {content}...")
        print("-" * 100)


def debug_vectorstore(vectorstore, question):
    print("\n[DEBUG 1] Verificando colección de Chroma")
    print("=" * 100)

    try:
        count = vectorstore._collection.count()
        print(f"Total de registros en Chroma: {count}")
    except Exception as e:
        print(f"No se pudo obtener count() de la colección: {e}")

    try:
        raw = vectorstore.get()
        total_docs = len(raw.get("documents", []))
        print(f"Total de documentos según vectorstore.get(): {total_docs}")
    except Exception as e:
        print(f"No se pudo ejecutar vectorstore.get(): {e}")

    print("\n[DEBUG 2] Probando similarity_search()")
    print("=" * 100)
    try:
        sim_docs = vectorstore.similarity_search(question, k=4)
        print_docs(sim_docs, "Resultados de similarity_search()")
    except Exception as e:
        print(f"Error en similarity_search(): {e}")

    print("\n[DEBUG 3] Probando retriever.invoke()")
    print("=" * 100)
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        retrieved_docs = retriever.invoke(question)
        print_docs(retrieved_docs, "Resultados de retriever.invoke()")
    except Exception as e:
        print(f"Error en retriever.invoke(): {e}")


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
            debug_vectorstore(vectorstore, question)

            print("\n[DEBUG 4] Ejecutando qa_chain.invoke()")
            print("=" * 100)

            response = qa_chain.invoke({"query": question})
            answer = response.get("result", "No se obtuvo respuesta.")
            sources = response.get("source_documents", [])

            print("\nRespuesta final:")
            print(answer)

            print_docs(sources, "Source documents devueltos por la chain", max_chars=250)

            print("\n" + "#" * 100 + "\n")

        except Exception as e:
            print(f"\nOcurrió un error general: {e}\n")


if __name__ == "__main__":
    main()