import json
import faiss
import os 
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "faiss.index"
META_PATH = ROOT / "data" / "chunk_metadata.json"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
GEMINI_MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
embed_model = SentenceTransformer(EMBED_MODEL_NAME)
faiss_index = faiss.read_index(str(INDEX_PATH))
with META_PATH.open(encoding="utf-8") as f:
      chunk_metadata = json.load(f)


def retrieve(query, k=4):
    query_vec = embed_model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(query_vec)
    scores, indices = faiss_index.search(query_vec, k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append({"score": float(score), **chunk_metadata[idx]})
    return results

def build_context(results):
        parts = []
        for i, r in enumerate(results, start=1):
            parts.append(f"[{i}] Source: {r['page_title']} - {r['section']}\nURL: {r['source_url']}\n{r['text']}")
        return "\n\n".join(parts)

def build_prompt(query, context):
           return f"""You are a helpful assistant that answers questions about FastAPI using ONLY the documentation excerpts provided below.

Rules:
- Answer using ONLY information from the excerpts below. Do not use any outside knowledge.
- Cite your sources using the excerpt numbers, like [1] or [2], right after the relevant claim.
- If the excerpts do not contain enough information to answer the question, say "I don't have enough information in the documentation to answer that" instead of guessing.
- Be concise and direct.

Documentation excerpts:
{context}

Question: {query}

Answer:"""

def generate_answer(query, k=4):
    results = retrieve(query, k=k)
    context = build_context(results)
    prompt = build_prompt(query, context)
    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
    )
    return {
        "answer": response.text,
        "sources": results,
    }


if __name__ == "__main__":
    test_query = "How do I declare the type of path parameter?"
    result = generate_answer(test_query, k=8)
    print("Question:", test_query)
    print("\nAnswer:\n", result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(f"  [{s['page_title']} - {s['section']}] {s['source_url']} (score: {s['score']:.3f})")
         
               
