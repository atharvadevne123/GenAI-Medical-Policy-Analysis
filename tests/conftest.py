import io
import struct
import zlib
import pytest
from unittest.mock import MagicMock, patch


# ── Minimal valid PDF bytes ───────────────────────────────────────────────────

def _make_pdf(text: str = "Sample medical policy text.") -> bytes:
    """Return a minimal single-page PDF that PyPDF2 can parse."""
    encoded = text.encode("latin-1", errors="replace")
    stream = zlib.compress(encoded)
    pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    )
    stream_obj = (
        b"4 0 obj\n<< /Filter /FlateDecode /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"\nendstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    )
    xref_offset = len(pdf) + len(stream_obj)
    trailer = (
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000266 00000 n \n"
        b"0000000360 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
        + str(xref_offset).encode()
        + b"\n%%EOF\n"
    )
    return pdf + stream_obj + trailer


@pytest.fixture
def sample_pdf() -> io.BytesIO:
    return io.BytesIO(_make_pdf())


@pytest.fixture
def mock_openai_response():
    """Patch OpenAI so no real API calls are made."""
    with patch("langchain_helper1.OpenAI") as MockCls:
        instance = MagicMock()
        instance.chat.completions.create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=(
                            "| Field | Aetna |\n"
                            "|---|---|\n"
                            "| Status | Active |\n"
                        )
                    )
                )
            ]
        )
        MockCls.return_value = instance
        yield instance


@pytest.fixture
def flask_client(mock_openai_response):
    """Flask test client with OpenAI mocked out."""
    import server
    server.app.config["TESTING"] = True
    with server.app.test_client() as client:
        yield client
