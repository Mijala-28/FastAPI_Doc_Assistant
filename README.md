# FastAPI Docs Assistant 📘

**[🔗 Try it live](https://fastapidocassistant-dibb9tsw4tqudwxu8bgj3k.streamlit.app/)**

A RAG (Retrieval-Augmented Generation) chatbot that answers developer questions about FastAPI using **only** the official documentation — with citations to the exact doc section, and an honest "I don't have enough information" when the docs don't cover something.

## Why this exists
Developers using FastAPI constantly hit specific questions ("how do I add a custom exception handler?", "how do I declare a path parameter with a type?"). Searching docs by hand is slow, and general-purpose chatbots can confidently make up framework-specific details that sound plausible but are wrong. Supports questions in multiple languages (tested with English and Nepali) — answers are generated in the same language as the question, while still grounded in the English documentation.

## Demo

*(Insert a short GIF or screen recording here showing a question, the cited answer, and the expanded "View sources" section)*

## How it works

1. **Data pipeline** — 110 pages of FastAPI's official docs (tutorial, advanced, how-to, deployment sections) are pulled from GitHub, cleaned (resolving custom code-include syntax, stripping HTML/admonition markup), and split into ~894 retrieval-sized chunks, each tagged with a source URL and section.
2.2. **Embedding + retrieval** — Each chunk is embedded with a multilingual `sentence-transformers` model (`paraphrase-multilingual-MiniLM-L12-v2`) and indexed in FAISS for fast semantic search. This means questions can be asked in languages other than English (tested with Nepali) while still retrieving from the English documentation correctly.
3. **Answer generation** — A user's question is embedded the same way, FAISS retrieves the top-k most relevant chunks, and Google's Gemini API generates an answer using *only* those chunks, citing which excerpt supports each claim.
4. **Conversation memory** — Follow-up questions ("what about for multiple exception types?") are resolved using recent conversation history, without letting the model treat its own earlier unverified claims as a source of truth.
5. **Interface** — A Streamlit chat UI displays the answer with inline `[1]`, `[2]` citations and an expandable, numbered "View sources" panel linking back to the live FastAPI docs.

## Project structure

*(`data/raw/`, `data/clean/`, and `docs_src/` are git-ignored — regenerate them by running `clean_docs.py`, `chunk_docs.py`, and `build_index.py` in order.)*

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows; use `source venv/bin/activate` on Mac/Linux
pip install -r requirements.txt
```

You'll also need a free [Google AI Studio](https://aistudio.google.com) API key. Create a `.env` file in the project root:

To rebuild the data pipeline from scratch:
```bash
python src/clean_docs.py
python src/chunk_docs.py
python src/build_index.py
```

To run the app locally:
```bash
streamlit run src/app.py
```
## Multilingual support

Added multilingual support by swapping the embedding model from
`all-MiniLM-L6-v2` to `paraphrase-multilingual-MiniLM-L12-v2` (rebuilding
the FAISS index), and adding one prompt rule instructing Gemini to respond
in the same language the question was asked in, while still grounding
answers in the English documentation.

Tested with a Nepali question ("मैले FastAPI मा path parameter को type
कसरी declare गर्ने?" — "How do I declare the type of a path parameter in
FastAPI?"):
- Retrieval correctly found the right English doc chunk (0.78 relevance,
  comparable to English-language queries)
- Gemini generated a fluent, correct Nepali answer with proper citations,
  synthesizing details from multiple sources

No separate translation step needed — the multilingual embedding model
handles cross-lingual retrieval, and Gemini handles cross-lingual
generation natively.

## Limitations & future improvements

- **Retrieval is sensitive to vocabulary overlap** between a user's phrasing and the docs' own wording. E.g., "automatic API documentation" scored 0.56 relevance and missed the best chunks, while "Swagger UI" (matching the docs' terminology) scored 0.82 and retrieved them correctly. Could be improved with query expansion or a larger embedding model.
- **Free-tier Gemini API** occasionally returns `503` errors under high demand; the app retries with exponential backoff, but a paid tier would be needed for production reliability.
- **Streamlit Community Cloud's free tier** sleeps after ~12 hours of inactivity — the first visit after a while may take 30-60 seconds to wake up.
- **No hybrid search** — currently pure semantic (embedding) search; adding keyword (BM25) matching alongside embeddings would likely improve retrieval for exact API names/terms.

See [`NOTES.md`](NOTES.md) for a detailed debugging log of real issues found and fixed while building this (including how a one-line indentation bug silently truncated context to Gemini, and how it was diagnosed).

## Tech stack

Python · sentence-transformers (multilingual) · FAISS · Google Gemini API · Streamlit · Streamlit Community Cloud