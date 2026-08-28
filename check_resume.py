#!/usr/bin/env python3
import subprocess
import sys
import os

def load_whitelist(path="whitelist.txt"):
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return {line.strip().lower() for line in f if line.strip() and not line.startswith("#")}

def get_page_count(pdf_path="resume.pdf"):
    result = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1].strip())
    return None

def extract_text(pdf_path="resume.pdf"):
    result = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True)
    return result.stdout

def check_grammar(text, whitelist):
    import language_tool_python
    tool = language_tool_python.LanguageTool("en-US")
    matches = tool.check(text)
    filtered = []
    for m in matches:
        offending = text[m.offset : m.offset + m.error_length].strip().lower()
        if offending in whitelist:
            continue
        filtered.append(m)
    return filtered

def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "resume.pdf"
    whitelist = load_whitelist()

    # Page count
    pages = get_page_count(pdf_path)
    page_ok = pages is not None and pages <= 1
    if pages is None:
        print(f"[WARN] Could not determine page count of {pdf_path}")
    elif page_ok:
        print(f"[PASS] Page count: {pages} page(s)")
    else:
        print(f"[FAIL] Resume is {pages} page(s) — should be 1 page or fewer")

    # Grammar
    print("Running grammar check (this may take a moment)...")
    text = extract_text(pdf_path)
    issues = check_grammar(text, whitelist)
    if not issues:
        print("[PASS] No grammar/spelling issues found")
    else:
        print(f"[FAIL] {len(issues)} grammar/spelling issue(s) found:")
        for m in issues:
            snippet = text[max(0, m.offset - 20) : m.offset + m.error_length + 20].replace("\n", " ")
            print(f"  - {m.message}")
            print(f"    Context: ...{snippet}...")

    # Exit code
    if not page_ok or issues:
        sys.exit(1)

if __name__ == "__main__":
    main()
