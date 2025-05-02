import boto3
import openai
import streamlit as st
import PyPDF2
import openai
import boto3
import io
import retrying
from openai import OpenAI
from PyPDF2 import PdfReader
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI()
# Use the OpenAI API key from the environment variable
openai_api_key = os.getenv('NA')
client = OpenAI(openai_api_key='NA')

# Ensure the OpenAI API key is provided
if not openai_api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")


def split_pdf_into_batches(bucket_name, common_string, batch_size):

 access_key = 'NA'
 secret_key = 'NA'

 s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
 try:
        # List objects in the S3 bucket that match the common string
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=common_string)

        if 'Contents' in response:
            # Iterate through the objects and read their content
            for obj in response['Contents']:
                file_name = obj['Key']
                # Read the file content
                response = s3.get_object(Bucket=bucket_name, Key=file_name)
                file_content = response['Body'].read()
                # Open the PDF file
                pdf_file = io.BytesIO(file_content)
                pdf_reader = PdfReader(pdf_file)

                # Initialize variables
                total_pages = len(pdf_reader.pages)
                current_page = 0

                while current_page < total_pages:
                    # Create a batch of text
                    text_batch = ''
                    while current_page < total_pages and len(text_batch) < batch_size:
                        page = pdf_reader.pages[current_page]
                        text_batch += page.extract_text()
                        current_page += 1

                    yield text_batch

                pdf_file.close()

 except Exception as e:
        print(e)
   
@retrying.retry(wait_fixed=1000, stop_max_attempt_number=3)  # Retry 3 times with a 1-second delay between retries   
def medical_cond_analysis(medical_condition, text_batch, openai_api_key):
    llm = OpenAI(temperature=0.7, openai_api_key= 'NA' )

    prompt_template_name = PromptTemplate(
        input_variables=['medical_condition' , 'text_batch'],
        template="I am a Hospital Medical Policy Analyst {medical_condition}. The {medical_condition} is for a patient. Act as a medical policy analyst, when I provide you with PDFs of medical policies pertaining to a specific medical condition from various insurance providers, please analyze and compare these policies in detail. Structure the information into a well-organized table, focusing on accuracy and specificity. Skip reading the "References" section in the documents. Use context-aware search and only read sections of the document that have info on the following fields. The comparison should include the following fields in the order:Policy Number: The unique identifier for each policy. Title: The official title of the policy. Policy Criteria: Key conditions or prerequisites for the policy's applicability. Age Criteria: Any age-related requirements for policy coverage. Insurance Company Name: Insurance company offering the policy. Insurance Type: The type of insurance (e.g., Commercial, Medicaid, Medicare Advantage). Service Type: Classification of the policy (Medical, Pharmacy, or Specialty Drug). Status: The current status of the policy (Active, Archived, Future). Effective Date: The date when the policy became effective. Last Review: The date of the most recent policy review. Next Review: The scheduled date for the next policy review. Guideline Source: The sources contributing to the policy. States Covered: The geographic regions or states where the policy applies. Needs Prior Authorization: Indication of whether the policy requires prior authorization (Yes/No), and any specific details if available. Exclusions/Limitations: Any exclusions or limitations outlined in the policy. Coverage Period: The start and end dates of the coverage period. Related Policies: Any linked or relevant policies. Link to Policy: A direct link or reference to the policy document. Note that some policies may not provide information for each category. In such cases, please indicate 'Not specified' in the relevant sections of the table."
    )

    # pdb.set_trace()
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name, output_key="policy_analysis")

    response = name_chain({'medical_condition': medical_condition, 'text_batch': text_batch})

    return response 

def __init__(self, openai_api_key: str):
    self.openai_api_key = openai_api_key    

# if __name__ == '__main__':
    # print(medical_cond_analysis('Cochlear Implantation'))
