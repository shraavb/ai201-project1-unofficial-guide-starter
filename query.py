import os
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

TOP_K = 3
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "syllabi"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a syllabus assistant for university courses. "
    "Answer questions ONLY using the retrieved syllabus excerpts provided in the user message. "
    "Do not use any outside or general knowledge. "
    "If the excerpts do not contain enough information to answer the question, respond with: "
    "'I could not find that information in the available syllabi.' "
    "Always end your answer by citing the source document(s) in brackets, "
    "e.g. [Source: FNCE101_Syllabus_Asher_F21.pdf]."
)


def build_context(documents: list, sources: list) -> str:
    parts = [f"[Source: {src}]\n{doc}" for doc, src in zip(documents, sources)]
    return "\n\n---\n\n".join(parts)


def query_system(question: str, collection, embed_model, llm):
    q_embed = embed_model.encode([question]).tolist()[0]
    results = collection.query(query_embeddings=[q_embed], n_results=TOP_K)

    docs = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    context = build_context(docs, sources)

    user_msg = f"RETRIEVED CONTEXT:\n{context}\n\nQUESTION: {question}"

    response = llm.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
    )

    answer = response.choices[0].message.content
    unique_sources = list(dict.fromkeys(sources))
    return answer, unique_sources


def main():
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not set. Add it to .env.")
        return

    print("Loading model and vector store...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
    except Exception:
        print("ERROR: Vector store not found. Run `python ingest.py` first.")
        return

    print(f"Syllabus Q&A ready ({collection.count()} chunks indexed). Type 'quit' to exit.\n")

    while True:
        question = input("Question: ").strip()
        if not question or question.lower() in ("quit", "exit", "q"):
            break

        answer, sources = query_system(question, collection, embed_model, groq_client)
        print(f"\n{answer}\n")
        print(f"Retrieved from: {', '.join(sources)}\n")
        print("-" * 60 + "\n")


if __name__ == "__main__":
    main()
