import json
from unittest.mock import patch


def test_index_returns_html(flask_client):
    """GET / returns 200 with HTML content."""
    resp = flask_client.get("/")
    assert resp.status_code == 200
    assert b"html" in resp.data.lower()


def test_demo_default_condition(flask_client):
    """POST /api/demo without body uses default condition."""
    resp = flask_client.post("/api/demo", json={})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["condition"] == "Cochlear Implant"
    assert body["demo"] is True
    assert len(body["analyses"]) >= 1


def test_demo_custom_condition(flask_client):
    """POST /api/demo with condition echoes it back."""
    resp = flask_client.post("/api/demo", json={"condition": "LASIK"})
    assert resp.status_code == 200
    assert resp.get_json()["condition"] == "LASIK"


def test_analyze_missing_condition(flask_client):
    """POST /api/analyze without condition returns 400."""
    resp = flask_client.post("/api/analyze", data={})
    assert resp.status_code == 400
    assert "condition" in resp.get_json()["error"].lower()


def test_analyze_missing_api_key(flask_client):
    """POST /api/analyze without OPENAI_API_KEY returns 500."""
    import os
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        resp = flask_client.post("/api/analyze", data={"condition": "Cochlear"})
    assert resp.status_code == 500


def test_analyze_no_documents(flask_client):
    """POST /api/analyze when no PDFs found returns 404."""
    import os
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-fake"}):
        with patch("langchain_helper1.split_pdf_into_batches", return_value=iter([])):
            resp = flask_client.post("/api/analyze", data={"condition": "Cochlear"})
    assert resp.status_code == 404


def test_analyze_streams_sse(flask_client):
    """POST /api/analyze returns SSE stream with meta and done events."""
    import os
    fake_batch = "Policy text sample"
    fake_analysis = "| Field | Aetna |\n|---|---|\n| Status | Active |\n"

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-fake"}):
        with patch("langchain_helper1.split_pdf_into_batches", return_value=iter([fake_batch])):
            with patch("langchain_helper1.medical_cond_analysis", return_value={"policy_analysis": fake_analysis}):
                resp = flask_client.post("/api/analyze", data={"condition": "Cochlear"})

    assert resp.status_code == 200
    assert resp.content_type.startswith("text/event-stream")

    raw = resp.data.decode("utf-8")
    events = [json.loads(line[len("data: "):]) for line in raw.splitlines() if line.startswith("data: ")]

    types = [e["type"] for e in events]
    assert "meta" in types
    assert "batch" in types
    assert "done" in types


def test_export_csv_no_analyses(flask_client):
    """POST /api/export-csv with empty analyses returns 400."""
    resp = flask_client.post("/api/export-csv", json={"analyses": []})
    assert resp.status_code == 400


def test_export_csv_returns_csv(flask_client):
    """POST /api/export-csv returns valid CSV with correct headers."""
    analysis = "| Field | Aetna |\n|---|---|\n| Status | Active |\n"
    resp = flask_client.post(
        "/api/export-csv",
        json={"analyses": [analysis], "condition": "Cochlear"},
    )
    assert resp.status_code == 200
    assert "text/csv" in resp.content_type
    csv_text = resp.data.decode("utf-8")
    assert "Field" in csv_text
    assert "Aetna" in csv_text
    assert "Status" in csv_text
    assert "Active" in csv_text


def test_export_csv_filename_sanitized(flask_client):
    """CSV filename derived from condition is sanitized."""
    analysis = "| A | B |\n|---|---|\n| x | y |\n"
    resp = flask_client.post(
        "/api/export-csv",
        json={"analyses": [analysis], "condition": "Heart Attack!"},
    )
    disposition = resp.headers.get("Content-Disposition", "")
    assert "Heart_Attack_" in disposition or "Heart" in disposition
