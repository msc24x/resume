#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import threading
import re
from pathlib import Path

ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

SCORE_DIR = Path(__file__).resolve().parent
BASE_DIR = SCORE_DIR.parent
RESUME_JSON = BASE_DIR / "resume_data.json"
RESUME_PDF = BASE_DIR / "resume.pdf"
SKILLS_MAP = SCORE_DIR / "skills_map.json"
GEN_SCRIPT = BASE_DIR / "generator" / "gen"
TEST_JD = SCORE_DIR / "test_jd.txt"
INDEX_HTML = SCORE_DIR / "index.html"

sys.path.insert(0, str(SCORE_DIR))
from score_resume import (  # noqa: E402
    score_resume,
    calc_experience,
    extract_required_years,
    format_report,
    load_skills_map,
)

app = FastAPI(title="Resume Scorer")

build_lock = threading.Lock()


def get_skills_map():
    return load_skills_map(str(SKILLS_MAP))


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(INDEX_HTML.read_text())


@app.get("/api/resume")
def api_resume():
    if not RESUME_JSON.exists():
        return JSONResponse({"ok": False, "error": "resume_data.json not found"}, status_code=404)
    return JSONResponse({"ok": True, "content": RESUME_JSON.read_text()})


@app.get("/api/jd")
def api_jd():
    content = TEST_JD.read_text() if TEST_JD.exists() else ""
    return JSONResponse({"ok": True, "content": content})


@app.post("/api/score")
async def api_score(req: Request):
    data = await req.json()
    resume_text = data.get("resume", "")
    jd_text = data.get("jd", "")
    try:
        resume_data = json.loads(resume_text)
    except json.JSONDecodeError as exc:
        return JSONResponse({"ok": False, "error": f"Invalid resume JSON: {exc}"}, status_code=400)

    skills_map = get_skills_map()
    years, months = calc_experience(resume_data.get("experience", []))
    jd_required = extract_required_years(jd_text)
    result = score_resume(resume_data, jd_text, skills_map, years=years, jd_required=jd_required)
    experience_info = {"your_experience": (years, months), "jd_required": jd_required}
    verbose = bool(data.get("verbose", False))
    report = format_report(result, experience_info, skills_map, verbose=verbose)
    report = ANSI_ESCAPE.sub('', report)

    return JSONResponse({
        "ok": True,
        "score": result["score"],
        "matched": len(result["matched"]),
        "missing": len(result["missing"]),
        "report": report,
    })


@app.post("/api/save")
async def api_save(req: Request):
    data = await req.json()
    resume_text = data.get("resume", "")
    try:
        json.loads(resume_text)
    except json.JSONDecodeError as exc:
        return JSONResponse({"ok": False, "error": f"Invalid resume JSON: {exc}"}, status_code=400)

    with build_lock:
        RESUME_JSON.write_text(resume_text)
        log = ""
        try:
            proc = subprocess.run(
                ["bash", str(GEN_SCRIPT)],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=180,
            )
            log = (proc.stdout or "") + (proc.stderr or "")
        except Exception as exc:  # noqa: BLE001
            log = f"Build error: {exc}"
        pdf_ok = RESUME_PDF.exists()

    return JSONResponse({
        "ok": pdf_ok,
        "pdfUrl": "/resume.pdf" if pdf_ok else None,
        "log": log,
    })


@app.get("/resume.pdf")
def serve_pdf():
    if not RESUME_PDF.exists():
        return JSONResponse({"error": "PDF not built yet"}, status_code=404)
    return FileResponse(str(RESUME_PDF), media_type="application/pdf", filename="resume.pdf")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
