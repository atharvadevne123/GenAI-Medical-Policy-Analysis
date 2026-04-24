import io
import os

import boto3
from openai import OpenAI
from PyPDF2 import PdfReader


def split_pdf_into_batches(bucket_name, common_string, batch_size):
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")

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
        print(e)


def analyze_text_batch(text_batch, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "As a medical policy analyst, perform a meticulous and detailed comparison of "
                    "medical policies across multiple insurance providers. Structure the information "
                    "into a well-organized Markdown table with fields: Policy Number, Title, "
                    "Policy Criteria, Age Criteria, Insurance Company Name, Insurance Type, "
                    "Service Type, Status, Link to Policy, Effective Date, Next Review, Last Review, "
                    "Guideline Source, States Covered, Needs Prior Authorization, "
                    "Exclusions/Limitations, Coverage Period, Related Policies. "
                    "Indicate 'Not specified' for missing fields."
                ),
            },
            {"role": "user", "content": text_batch},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    bucket_name = "policydocumentschiesta"
    common_string = "Cochlear"
    batch_size = 4000

    for text_batch in split_pdf_into_batches(bucket_name, common_string, batch_size):
        print(analyze_text_batch(text_batch, openai_api_key))
