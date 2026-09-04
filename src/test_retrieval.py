import json
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "faiss.index"
META_PATH = ROOT / "data" / "chunk_metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"

def search(query, k=4):
    model = SentenceTransformer(MODEL_NAME)
    index = faiss.read_index(str(INDEX_PATH))
    with META_PATH.open(encoding="utf-8") as f:
        metadata = json.load(f)

    query_vec = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        chunk = metadata[idx]
        results.append((float(score), chunk))
    return results

if __name__ == "__main__":
    test_query = "How do I add a path parameter with type validation?"
    results = search(test_query)

    print(f"Query: {test_query}\n")
    for score, chunk in results:
        print(f"Score: {score:.3f} | {chunk['page_title']} > {chunk['section']}")
        print(f"URL: {chunk['source_url']}")
        print(chunk['text'][:200])
        print("---")

        