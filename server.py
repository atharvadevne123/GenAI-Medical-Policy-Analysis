import csv
import io
import json
import os
import re
import tempfile

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context

import langchain_helper1 as lch

load_dotenv()

app = Flask(__name__, static_folder="ui", static_url_path="/ui")


# ── Static pages ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("ui", "index.html")


# ── Demo ──────────────────────────────────────────────────────────────────────

@app.route("/api/demo", methods=["POST"])
def demo():
    condition = (request.json or {}).get("condition", "Cochlear Implant")
    return jsonify({
        "condition": condition,
        "batches": 1,
        "analyses": [lch.DEMO_ANALYSIS],
        "demo": True,
    })


# ── Live analysis (SSE streaming) ─────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze():
    condition = request.form.get("condition", "").strip()
    if not condition:
        return jsonify({"error": "Medical condition is required"}), 400

    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_api_key:
        return jsonify({"error": "OPENAI_API_KEY not configured on server"}), 500

    uploaded_files = request.files.getlist("pdfs")
    tmp_paths = []
    tmp_handles = []

    try:
        if uploaded_files and uploaded_files[0].filename:
            for f in uploaded_files:
                tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                f.save(tmp.name)
                tmp.flush()
                tmp_paths.append(tmp.name)
                tmp_handles.append(open(tmp.name, "rb"))

        batches = list(
            lch.split_pdf_into_batches(
                bucket_name="policydocumentschiesta",
                common_string=condition,
                batch_size=4000,
                uploaded_files=tmp_handles if tmp_handles else None,
            )
        )
    finally:
        for fh in tmp_handles:
            fh.close()
        for path in tmp_paths:
            try:
                os.unlink(path)
            except OSError:
                pass

    if not batches:
        return jsonify({"error": "No policy documents found. Upload PDFs or check S3 config."}), 404

    def generate():
        yield _sse({"type": "meta", "total": len(batches), "condition": condition})
        for i, batch in enumerate(batches):
            try:
                result = lch.medical_cond_analysis(condition, batch, openai_api_key)
                yield _sse({
                    "type": "batch",
                    "index": i + 1,
                    "total": len(batches),
                    "analysis": result["policy_analysis"],
                })
            except Exception as e:
                yield _sse({"type": "error", "index": i + 1, "message": str(e)})
        yield _sse({"type": "done", "total": len(batches)})

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


# ── CSV export ────────────────────────────────────────────────────────────────

@app.route("/api/export-csv", methods=["POST"])
def export_csv():
    body = request.get_json(silent=True) or {}
    analyses = body.get("analyses", [])
    condition = body.get("condition", "export")

    if not analyses:
        return jsonify({"error": "No analyses provided"}), 400

    csv_text = _markdown_tables_to_csv(analyses)
    filename = re.sub(r"[^\w\-]", "_", condition) + ".csv"

    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _markdown_tables_to_csv(analyses: list) -> str:
    output = io.StringIO()
    writer = None
    header_written = False

    for analysis in analyses:
        for line in analysis.splitlines():
            line = line.strip()
            if not line:
                continue
            # Skip separator rows like |---|---|
            if re.match(r"^\|[\s\-\|]+\|$", line):
                continue
            if line.startswith("|") and line.endswith("|"):
                cells = [c.strip().lstrip("*").rstrip("*") for c in line[1:-1].split("|")]
                if writer is None:
                    writer = csv.writer(output)
                if not header_written:
                    writer.writerow(cells)
                    header_written = True
                else:
                    writer.writerow(cells)

    return output.getvalue()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting GenAI Medical Policy Analyzer on http://localhost:{port}")
    app.run(debug=False, host="0.0.0.0", port=port)
