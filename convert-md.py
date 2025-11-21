#!/usr/bin/env python3
import re
import json
import os
import sys

# === CONFIGURATION ===
INPUT_FILE = "1905 Naga Hills and Manipur by Allen s.md"          # Input .md file
MAX_TOKENS = 200

# --- Token counter ---
def get_token_counter():
    try:
        import tiktoken
    except ImportError:
        sys.exit("Install tiktoken: pip install tiktoken")
    enc = tiktoken.get_encoding("cl100k_base")
    return lambda text: len(enc.encode(text))

token_count = get_token_counter()

# --- Cleaning ---
def clean_text(text):
    """Clean unwanted markdown, HTML, and escaped noise."""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)           # remove image markdown
    text = re.sub(r'\\"', '"', text)                      # remove escaped quotes
    text = re.sub(r"\[\*.*?\*\]", "", text)
    text = re.sub(r"\*\*\*.*?\*\*\*", "", text)
    text = re.sub(r"<sup>.*?</sup>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"\\[*_`]+", "", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"[\r\n]+", " ", text)
    return text.strip()

# --- Detect if content is a table ---
def is_table(lines):
    """Check if lines contain a markdown table."""
    if not lines:
        return False
    # Check if at least one line matches table pattern
    table_lines = [line for line in lines if TABLE_ROW_RE.match(line)]
    return len(table_lines) >= 2  # At least header + one row

# --- Parse table rows ---
def parse_table_rows(lines):
    """Parse markdown table into list of row data."""
    rows = []
    for line in lines:
        if TABLE_ROW_RE.match(line):
            # Skip separator lines (e.g., |---|---|)
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                continue
            # Extract cell data
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and any(cell for cell in cells):  # Skip empty rows
                rows.append(cells)
    return rows

# --- Split text ---
def split_by_tokens(text, max_tokens):
    words = text.split()
    chunks, current = [], []
    for w in words:
        candidate = " ".join(current + [w])
        if token_count(candidate) <= max_tokens:
            current.append(w)
        else:
            chunks.append(" ".join(current))
            current = [w]
    if current:
        chunks.append(" ".join(current))
    return chunks

# --- Regex patterns ---
MARKDOWN_HEADING_RE = re.compile(r'^\s*(#{1,6})\s*(.*)$')
SECTION_RE = re.compile(r'^\s*#+\s*\*\*(\d+[A-Z]?\. .+?)\*\*', re.UNICODE)
TABLE_ROW_RE = re.compile(r'^\s*\|.*\|\s*$')

# --- Parse markdown ---
def parse_markdown(md_text):
    lines = md_text.splitlines()
    sections = []
    stack, buffer = [], []

    def flush_buffer():
        if buffer:
            title = " / ".join(stack)
            # Check if buffer contains a table
            if is_table(buffer):
                table_rows = parse_table_rows(buffer)
                sections.append({"Title": title, "content": buffer, "is_table": True, "table_rows": table_rows})
            else:
                content = clean_text(" ".join(buffer))
                if content:
                    sections.append({"Title": title, "content": content, "is_table": False})
            buffer.clear()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # Skip image or noise lines
        if re.match(r"!\[.*?\]\(.*?\)", line):
            continue
        if re.match(r"^\*+\s*\d*\s*\*+\s*\*+$", line):
            continue

        # Main heading
        m_head = MARKDOWN_HEADING_RE.match(line)
        if m_head and not SECTION_RE.match(line):
            flush_buffer()
            level = len(m_head.group(1))
            title_text = clean_text(m_head.group(2))
            while len(stack) >= level:
                stack.pop()
            stack.append(title_text)
            continue

        # Numbered section
        m_sec = SECTION_RE.match(line)
        if m_sec:
            flush_buffer()
            while len(stack) > 3:
                stack.pop()
            stack.append(clean_text(m_sec.group(1)))
            continue

        buffer.append(line)

    flush_buffer()
    return sections

# --- Convert one file ---
def md_to_json(input_path, output_path):
    with open(input_path, encoding="utf-8") as f:
        text = f.read()

    sections = parse_markdown(text)
    json_data = []

    for sec in sections:
        if sec.get("is_table", False):
            # For tables, create one object per row without token limit
            table_rows = sec.get("table_rows", [])
            for row in table_rows:
                json_data.append({
                    "title": sec["Title"],
                    "content": " | ".join(row),
                    "is_table": True
                })
        else:
            # For non-table content, split by tokens
            chunks = split_by_tokens(sec["content"], MAX_TOKENS)
            for chunk in chunks:
                json_data.append({
                    "title": sec["Title"],
                    "content": chunk.strip(),
                    "is_table": False
                })

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(json_data, out, ensure_ascii=False, indent=2)

    print(f"✅ {os.path.basename(output_path)} — {len(json_data)} JSON objects saved.")

# --- Main ---
if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        sys.exit(f"[ERROR] File not found: {INPUT_FILE}")

    if not INPUT_FILE.lower().endswith(".md"):
        sys.exit(f"[ERROR] Input file must be a .md file: {INPUT_FILE}")

    output_path = os.path.splitext(INPUT_FILE)[0] + ".json"
    md_to_json(INPUT_FILE, output_path)
