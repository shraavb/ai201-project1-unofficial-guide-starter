import os
import re
import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb

DOCS_DIR = "documents"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "syllabi"


def extract_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split(text: str, chunk_size: int, overlap: int, separators: list) -> list:
    if not text.strip():
        return []
    if len(text) <= chunk_size:
        return [text.strip()]

    sep = separators[0]
    rest = separators[1:]

    if sep == "":
        chunks = []
        start = 0
        while start < len(text):
            chunk = text[start : start + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    parts = text.split(sep)
    if len(parts) == 1:
        return _split(text, chunk_size, overlap, rest)

    result = []
    current = ""

    for part in parts:
        candidate = (current + sep + part) if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                result.append(current.strip())
                overlap_text = current[-overlap:] if overlap < len(current) else current
                current = overlap_text + sep + part
                if len(current) > chunk_size:
                    sub = _split(current, chunk_size, overlap, rest)
                    result.extend(sub[:-1])
                    current = sub[-1] if sub else ""
            else:
                result.extend(_split(part, chunk_size, overlap, rest))
                current = ""

    if current.strip():
        result.append(current.strip())

    return [c for c in result if c.strip()]


def recursive_split(text: str) -> list:
    return _split(text, CHUNK_SIZE, CHUNK_OVERLAP, ["\n\n", "\n", ". ", " ", ""])


def main():
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    total_chunks = 0

    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".pdf"):
            continue

        path = os.path.join(DOCS_DIR, filename)
        print(f"Processing: {filename}")

        raw = extract_text(path)
        clean = clean_text(raw)
        chunks = recursive_split(clean)

        if not chunks:
            print("  WARNING: no chunks produced")
            continue

        embeddings = model.encode(chunks).tolist()
        ids = [f"{filename}::{i}" for i in range(len(chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]

        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas,
        )
        print(f"  {len(chunks)} chunks added")
        total_chunks += len(chunks)

    print(f"\nDone. {total_chunks} total chunks stored in ChromaDB at {CHROMA_PATH}/")


if __name__ == "__main__":
    main()
