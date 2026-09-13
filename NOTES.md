# Project Notes & Debugging Log

Keeping this as a running log of real issues found and fixed while building
this project — useful for the README's "Limitations" section and for
talking through the project in interviews.

## Bugs found and fixed

1. **Indentation bug in `build_context()` (Day 4)** — a `return` statement
   was nested one level too deep, inside the `for` loop instead of after it.
   This caused only the FIRST retrieved chunk to ever reach the LLM, even
   though retrieval was correctly finding all k chunks. Symptom: answers
   were oddly cautious / said "I don't have enough information" even when
   relevant chunks existed. Found by adding a debug print of the exact
   prompt sent to Gemini, rather than guessing.

2. **Missing `retrieve()` function (Day 5)** — got accidentally deleted
   while editing nearby code, causing a `NameError`. Fixed by re-adding it
   and verifying with `Select-String -Pattern "^def "` to list all function
   definitions and confirm none were missing.

3. **Leading space in `.gitignore`** — `.env` was still showing up as
   untracked despite being listed in `.gitignore`, because the line had a
   leading space (" .env" instead of ".env"), which git treats as a
   completely different, non-matching pattern.

4. **Missing `docs_src/` folder (Day 1)** — FastAPI's docs reference code
   examples via a custom `{* path *}` include syntax pointing to a separate
   `docs_src/` folder in the repo, which isn't included if you only clone
   `docs/`. Caught by manually inspecting a raw doc file before writing the
   cleaning script, rather than assuming a simple scrape would be complete.

## Retrieval quality findings

Retrieval confidence (cosine similarity score) is sensitive to vocabulary
overlap between the user's question and the documentation's own wording,
even when the underlying facts are the same.

Example:
- Query: "What is automatic API documentation?"
  → best relevance score: 0.56, retrieved mostly irrelevant `APIRouter` chunks
- Query: "Does FastAPI generate a Swagger UI automatically?"
  → best relevance score: 0.82, retrieved the correct chunks, complete answer

**Why this happens:** the embedding model measures semantic similarity, but
short queries with generic phrasing ("documentation") can be less
distinctive than domain-specific terms the docs actually use ("Swagger UI",
"OpenAPI schema").

**Possible improvements with more time:**
- Query expansion: have the LLM rewrite/expand the user's question with
  synonyms before embedding it
- A larger or fine-tuned embedding model
- Hybrid search combining keyword (BM25) + embedding similarity

## Design decisions worth explaining

- **IndexFlatIP over an approximate FAISS index**: at ~900 chunks, exact
  search is fast enough that approximate indexing (e.g. IVF) isn't needed.
  Chose simplicity and exactness over premature optimization.
- **Prompt explicitly separates conversation history (for resolving
  pronouns/references) from the documentation context (the only allowed
  source of facts)** — prevents the model from "remembering" its own
  earlier unverified claims as if they were documentation.
- **Free-tier Gemini API** chosen deliberately for a portfolio project to
  avoid cost, with the tradeoff understood: not suitable for production
  traffic volume.
  