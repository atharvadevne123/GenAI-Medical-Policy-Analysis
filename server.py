import json
import os
import tempfile

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

import langchain_helper1 as lch

load_dotenv()

app = Flask(__name__, static_folder="ui", static_url_path="/ui")


@app.route("/")
def index():
    return send_from_directory("ui", "index.html")


@app.route("/results")
def results():
    return send_from_directory("ui", "results.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    condition = request.form.get("condition", "").strip()
    if not condition:
        return jsonify({"error": "Medical condition is required"}), 400

    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_api_key:
        return jsonify({"error": "OPENAI_API_KEY not configured on server"}), 500

    uploaded_files = request.files.getlist("pdfs")
    tmp_files = []

    try:
        if uploaded_files and uploaded_files[0].filename:
            for f in uploaded_files:
                tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                f.save(tmp.name)
                tmp.flush()
                tmp_files.append(open(tmp.name, "rb"))

        batches = list(
            lch.split_pdf_into_batches(
                bucket_name="policydocumentschiesta",
                common_string=condition,
                batch_size=4000,
                uploaded_files=tmp_files if tmp_files else None,
            )
        )

        if not batches:
            return jsonify({"error": "No policy documents found. Upload PDFs or check S3 config."}), 404

        results = []
        for batch in batches:
            result = lch.medical_cond_analysis(condition, batch, openai_api_key)
            results.append(result["policy_analysis"])

        return jsonify({
            "condition": condition,
            "batches": len(results),
            "analyses": results,
        })

    finally:
        for f in tmp_files:
            fname = f.name
            f.close()
            try:
                os.unlink(fname)
            except OSError:
                pass


@app.route("/api/demo", methods=["POST"])
def demo():
    condition = request.json.get("condition", "Cochlear Implant")
    return jsonify({
        "condition": condition,
        "batches": 1,
        "analyses": [lch.DEMO_ANALYSIS],
        "demo": True,
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting GenAI Medical Policy Analyzer on http://localhost:{port}")
    app.run(debug=False, host="0.0.0.0", port=port)
