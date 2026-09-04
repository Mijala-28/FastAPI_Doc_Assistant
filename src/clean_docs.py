import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT/ "data" /"raw"
CLEAN_DIR = ROOT / "data" /"clean"
CODE_SRC_DIR = ROOT / "docs_src"
INCLUDE_RE = re.compile(r"\{\*\s*(\.\./\.\./docs_src/[^\s*]+)(?:\s+[^*]*)?\*\}")
HEADING_ID_RE = re.compile(r"\s*\{\s*#[\w\-]+\s*\}")

def resolve_code_include(match):
    rel_path = match.group(1).replace("../../docs_src/","")
    code_file = CODE_SRC_DIR / rel_path
    if not code_file.exists():
        return()
    code = code_file.read_text(encoding="utf-8", errors="ignore").rstrip()
    lang = "python" if code_file.suffix == ".py" else code_file.suffix.lstrip(".")
    return f"'''{lang}\n{code}\n'''"

ADMONITION_OPEN_RE = re.compile(r"^///\s*(tip|note|warning|info|danger|check)\b.*$", re.IGNORECASE)
ADMONITION_CLOSE_RE = re.compile(r"^///\s*$")

def clean_admonitions(lines):
    out = []
    i = 0
    while i < len(lines):
        m = ADMONITION_OPEN_RE.match(lines[i].strip())
        if m:
            label = m.group(1).capitalize()
            i += 1
            body = []
            while i < len(lines) and not ADMONITION_CLOSE_RE.match(lines[i].strip()):
                body.append(lines[i])
                i += 1
            i += 1
            out.append(f"**{label}:** {' '.join(body).strip()}")
        else:
            out.append(lines[i])
            i += 1
    return out

def clean_markdown(text):
    text = INCLUDE_RE.sub(resolve_code_include, text)
    lines = clean_admonitions(text.split("\n"))
    text = "\n".join(lines)
    text = re.sub(r"<[^>]+>", "", text)
    text = HEADING_ID_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"

def main():
    md_files = sorted(RAW_DIR.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files to clean.")
    for f in md_files:
        rel = f.relative_to(RAW_DIR)
        out_path = CLEAN_DIR / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        raw_text = f.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_markdown(raw_text)
        out_path.write_text(cleaned, encoding="utf-8")
    print(f"Wrote cleaned files to {CLEAN_DIR}")

if __name__ == "__main__":
    main()