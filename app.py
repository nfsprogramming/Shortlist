"""Flask server: serves the UI and exposes the screening API."""
import os

from flask import Flask, jsonify, request, send_from_directory

from engine import ResumeError, analyze, clean_text, extract_text, load_jobs

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB uploads


def error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "jobs": len(load_jobs())})


@app.get("/api/jobs")
def jobs():
    return jsonify(load_jobs())


@app.post("/api/analyze")
def analyze_resume():
    upload = request.files.get("resume")
    pasted = request.form.get("resume_text", "")
    jd = clean_text(request.form.get("job_description", ""))
    try:
        if upload and upload.filename:
            resume = extract_text(upload.filename, upload.read())
        elif pasted.strip():
            resume = clean_text(pasted)
            if len(resume) < 40:
                raise ResumeError("The resume text is too short to analyse.")
        else:
            raise ResumeError("Upload a resume or paste its text first.")
    except ResumeError as exc:
        return error(str(exc))
    return jsonify(analyze(resume, jd))


@app.errorhandler(413)
def too_large(_):
    return error("File is too large. The limit is 5 MB.", 413)


@app.errorhandler(404)
def not_found(_):
    return error("Not found.", 404)


if __name__ == "__main__":
    if os.environ.get("VERCEL"):
        import sys
        sys.exit(0)
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
