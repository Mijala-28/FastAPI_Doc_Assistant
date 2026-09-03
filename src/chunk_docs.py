import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = ROOT /"data" / "clean" 
OUT_PATH = ROOT /"data"/"chunks.jsonl"''''''
DOC_BASE_URL = "https://fastapi.tiangolo.com/"
MAX_CHUNK_WORDS = 300 
MIN_CHUNK_WORDS = 40 

HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$", re.MULTILINE)

def file_to_url(rel_path):
        parts = rel_path.with_suffix("").parts
        if parts[-1] == "index":
                  parts = parts[:-1]
        return DOC_BASE_URL + "/".join(parts) + "/"

def split_by_heading(text):
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        yield "", text.strip()
        return
    if matches[0].start() > 0:
        yield "", text[:matches[0].start()].strip()
    for i, m in enumerate(matches):
        heading = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield heading, text[start:end].strip()

def split_long_section(text, max_words):
    paras = [p for p in text.split("\n\n") if p.strip()]
    chunk, count = [], 0
    for p in paras:
        n = len(p.split())
        if count + n > max_words and chunk:
            yield "\n\n".join(chunk)
            chunk, count = [], 0
        chunk.append(p)
        count += n
    if chunk:
        yield "\n\n".join(chunk)

def main():
    files = sorted(CLEAN_DIR.rglob("*.md"))
    chunks = []

    for f in files:
        rel = f.relative_to(CLEAN_DIR)
        url = file_to_url(rel)
        page_title = rel.stem.replace("-", " ").title()
        text = f.read_text(encoding="utf-8")

        pending_heading, pending_text = None, ""
        for heading, section_text in split_by_heading(text):
            if not section_text:
                continue
            words = len(section_text.split())

            if words < MIN_CHUNK_WORDS:
                pending_heading = pending_heading or heading
                pending_text = (pending_text + "\n\n" + section_text).strip()
                continue

            if pending_text:
                section_text = (pending_text + "\n\n" + section_text).strip()
                heading = pending_heading or heading
                pending_heading, pending_text = None, ""

            if len(section_text.split()) > MAX_CHUNK_WORDS:
                for sub in split_long_section(section_text, MAX_CHUNK_WORDS):
                    chunks.append({
                        "text": sub,
                        "source_file": str(rel),
                        "source_url": url,
                        "page_title": page_title,
                        "section": heading,
                    })
            else:
                chunks.append({
                    "text": section_text,
                    "source_file": str(rel),
                    "source_url": url,
                    "page_title": page_title,
                    "section": heading,
                })

        if pending_text and len(pending_text.split()) >= 10:
            chunks.append({
                "text": pending_text,
                "source_file": str(rel),
                "source_url": url,
                "page_title": page_title,
                "section": pending_heading or "",
            })

    for i, c in enumerate(chunks):
        c["chunk_id"] = i

    with OUT_PATH.open("w", encoding="utf-8") as out:
        for c in chunks:
            out.write(json.dumps(c, ensure_ascii=False) + "\n")

    word_counts = [len(c["text"].split()) for c in chunks]
    print(f"{len(files)} files -> {len(chunks)} chunks")
    print(f"chunk size (words): min={min(word_counts)} max={max(word_counts)} avg={sum(word_counts)//len(word_counts)}")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()