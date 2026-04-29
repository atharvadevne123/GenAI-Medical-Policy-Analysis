from unittest.mock import MagicMock, patch


def test_split_pdf_local_upload(sample_pdf):
    """split_pdf_into_batches yields at least one batch from an uploaded file."""
    import langchain_helper1 as lch

    fake_page = MagicMock()
    fake_page.extract_text.return_value = "Sample medical policy text."
    fake_reader = MagicMock()
    fake_reader.pages = [fake_page]

    with patch("langchain_helper1.PdfReader", return_value=fake_reader):
        batches = list(
            lch.split_pdf_into_batches(
                bucket_name="unused",
                common_string="Cochlear",
                batch_size=4000,
                uploaded_files=[sample_pdf],
            )
        )
    assert len(batches) >= 1
    assert isinstance(batches[0], str)
    assert "Sample medical policy text." in batches[0]


def test_split_pdf_no_files_no_credentials():
    """split_pdf_into_batches returns empty list when S3 creds are missing."""
    import langchain_helper1 as lch

    with patch("langchain_helper1.boto3.client") as mock_boto:
        mock_boto.side_effect = Exception("No credentials")
        batches = list(
            lch.split_pdf_into_batches(
                bucket_name="nonexistent-bucket",
                common_string="Cochlear",
                batch_size=4000,
                uploaded_files=None,
            )
        )
    assert batches == []


def test_medical_cond_analysis_returns_markdown(mock_openai_response):
    """medical_cond_analysis returns dict with policy_analysis key."""
    import langchain_helper1 as lch

    mock_openai_response.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="| Field | Aetna |\n|---|---|\n| Status | Active |\n"))]
    )

    with patch("langchain_helper1.OpenAI", return_value=mock_openai_response):
        result = lch.medical_cond_analysis("Cochlear Implant", "some text", "fake-key")

    assert "policy_analysis" in result
    assert "Aetna" in result["policy_analysis"]


def test_demo_analysis_is_markdown_table():
    """DEMO_ANALYSIS constant contains at least one markdown table row."""
    import langchain_helper1 as lch

    assert "|" in lch.DEMO_ANALYSIS


def test_split_pdf_batch_size_respected(sample_pdf):
    """Batches are capped at batch_size characters."""
    import langchain_helper1 as lch

    long_text = "A" * 300
    fake_page = MagicMock()
    fake_page.extract_text.return_value = long_text
    fake_reader = MagicMock()
    fake_reader.pages = [fake_page]

    small_batch = 100
    with patch("langchain_helper1.PdfReader", return_value=fake_reader):
        batches = list(
            lch.split_pdf_into_batches(
                bucket_name="unused",
                common_string="test",
                batch_size=small_batch,
                uploaded_files=[sample_pdf],
            )
        )
    assert len(batches) >= 2
    for batch in batches[:-1]:
        assert len(batch) <= small_batch
