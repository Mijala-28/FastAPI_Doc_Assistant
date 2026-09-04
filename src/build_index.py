import json
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
CHUNKS_PATH = ROOT / "data" / "chunks.jsonl"
INDEX_PATH = ROOT / "data" / "faiss.index"
META_PATH = ROOT / "data" / "chunk_metadata.json"

MODEL_NAME = "all-MiniLM-L6-v2"

def load_chunks():
    chunks = []
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks

def main():
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")

    model = SentenceTransformer(MODEL_NAME)
    texts = [c["text"] for c in chunks]

    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype("float32")
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))

    metadata = [
        {
            "chunk_id": c["chunk_id"],
            "text": c["text"],
            "source_url": c["source_url"],
            "page_title": c["page_title"],
            "section": c["section"],
        }
        for c in chunks
    ]
    with META_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Built FAISS index with {index.ntotal} vectors of dimension {dimension}")
    print(f"Saved index to {INDEX_PATH}")
    print(f"Saved metadata to {META_PATH}")


if __name__ == "__main__":
    main()
