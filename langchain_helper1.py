import boto3
import io
import os

import retrying
from PyPDF2 import PdfReader
from openai import OpenAI


def split_pdf_into_batches(bucket_name, common_string, batch_size, uploaded_files=None):
    """Yield text batches from uploaded files (local) or S3."""
    if uploaded_files:
        for f in uploaded_files:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
                if len(text) >= batch_size:
                    yield text[:batch_size]
                    text = text[batch_size:]
            if text:
                yield text
        return

    access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    if not access_key or not secret_key:
        return

    s3 = boto3.client("s3", aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=common_string)
        if "Contents" not in response:
            return
        for obj in response["Contents"]:
            file_name = obj["Key"]
            resp = s3.get_object(Bucket=bucket_name, Key=file_name)
            file_content = resp["Body"].read()
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            current_page = 0
            while current_page < total_pages:
                text_batch = ""
                while current_page < total_pages and len(text_batch) < batch_size:
                    text_batch += pdf_reader.pages[current_page].extract_text() or ""
                    current_page += 1
                yield text_batch
            pdf_file.close()
    except Exception as e:
        print(f"S3 error: {e}")


@retrying.retry(wait_fixed=1000, stop_max_attempt_number=3)
def medical_cond_analysis(medical_condition, text_batch, openai_api_key):
    """Analyze policy text and return a markdown comparison table."""
    client = OpenAI(api_key=openai_api_key)

    system_prompt = (
        "You are a Hospital Medical Policy Analyst. "
        "Analyze the provided medical policy document text and produce a detailed comparative "
        "analysis table in Markdown format. "
        "Include these columns: Policy Number, Title, Policy Criteria, Age Criteria, "
        "Insurance Company Name, Insurance Type, Service Type, Status, Effective Date, "
        "Last Review, Next Review, Guideline Source, States Covered, "
        "Needs Prior Authorization, Exclusions/Limitations, Coverage Period, Related Policies. "
        "If a field is absent from the document, write 'Not specified'."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Medical Condition: {medical_condition}\n\n"
                    f"Policy Document Content:\n{text_batch}"
                ),
            },
        ],
        max_tokens=2000,
        temperature=0.3,
    )
    return {"policy_analysis": response.choices[0].message.content}


DEMO_ANALYSIS = """
| Field | Aetna Commercial Plan | UnitedHealth Medicare Advantage | Cigna PPO Plan |
|---|---|---|---|
| **Policy Number** | AET-COC-4521 | UH-COC-2023-881 | CIG-COC-7734 |
| **Title** | Cochlear Implant Coverage Policy | Cochlear Implantation | Cochlear Devices Coverage |
| **Policy Criteria** | Bilateral profound SNHL; failed hearing aids ≥ 3 months | Severe-to-profound SNHL; audiological workup required | Profound hearing loss; ENT referral required |
| **Age Criteria** | 12 months and older | 18 months and older | 12 months and older |
| **Insurance Company** | Aetna | UnitedHealth Group | Cigna |
| **Insurance Type** | Commercial | Medicare Advantage | Commercial PPO |
| **Service Type** | Medical | Medical | Medical |
| **Status** | Active | Active | Active |
| **Effective Date** | 2023-01-01 | 2022-07-01 | 2023-03-01 |
| **Last Review** | 2023-11-15 | 2023-08-20 | 2023-10-01 |
| **Next Review** | 2024-11-15 | 2024-08-20 | 2024-10-01 |
| **Guideline Source** | AAO-HNS, FDA guidelines | CMS, AAO-HNS | AAO-HNS clinical guidelines |
| **States Covered** | All 50 US States | AL, AZ, CA, FL, TX, NY | All 50 US States |
| **Prior Authorization** | Yes | Yes | Yes |
| **Exclusions** | Bilateral CI without documented unilateral benefit failure | Prior CI failure; non-compliant patients | Patients who have not trialed hearing aids ≥ 6 months |
| **Coverage Period** | Calendar year (annual renewal) | Annual (Jan–Dec) | Calendar year |
| **Related Policies** | AET-AUD-1102 (Hearing Aids) | UH-HRG-0042 | CIG-ENT-3301 |
"""
