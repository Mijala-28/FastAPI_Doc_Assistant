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

def build_retrieval_query(query, history, window=2):
    if not history:
        return query
    recent_user_turns = [h["content"] for h in history[-window:] if h["role"] == "user"]
    return " ".join(recent_user_turns) + " " + query

def build_context(results):
        parts = []
        for i, r in enumerate(results, start=1):
            parts.append(f"[{i}] Source: {r['page_title']} - {r['section']}\nURL: {r['source_url']}\n{r['text']}")
        return "\n\n".join(parts)

def build_prompt(query, context, history=None):
    history_text = ""
    if history:
        lines = []
        for h in history[-4:]:
            role = "User" if h["role"] == "user" else "Assistant"
            lines.append(f"{role}: {h['content']}")
        history_text = "Previous conversation:\n" + "\n".join(lines) + "\n\n"

    return f"""You are a helpful assistant that answers questions about FastAPI using ONLY the documentation excerpts provided below.

Rules:
- Answer using ONLY information from the excerpts below. Do not use any outside knowledge.
- Cite your sources using the excerpt numbers, like [1] or [2], right after the relevant claim.
- If the excerpts do not contain enough information to answer the question, say "I don't have enough information in the documentation to answer that" instead of guessing.
- Use the previous conversation only to understand what the user is referring to (e.g. "it", "that", "the same thing") - still answer strictly from the excerpts.
- Be concise and direct.

{history_text}Documentation excerpts:
{context}

Question: {query}

Answer:"""

def generate_answer(query, history=None, k=4):
    retrieval_query = build_retrieval_query(query, history or [])
    results = retrieve(retrieval_query, k=k)
    context = build_context(results)
    prompt = build_prompt(query, context, history=history)
    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
    )
    return {
        "answer": response.text,
        "sources": results,
    }

if __name__ == "__main__":
    history = []
    conversation = [
        "How do I add a custom exception handler?",
        "What about for multiple exception types?",
        "Can I do the same thing for HTTP errors specifically?",
    ]
    for q in conversation:
        result = generate_answer(q, history=history, k=6)
        print("=" * 60)
        print("User:", q)
        print("\nAssistant:\n", result["answer"])
        print("\nSources checked:")
        for s in result["sources"]:
            print(f"  [{s['page_title']} - {s['section']}] (score: {s['score']:.3f})")
        history.append({"role": "user", "content": q})
        history.append({"role": "assistant", "content": result["answer"]})
               
