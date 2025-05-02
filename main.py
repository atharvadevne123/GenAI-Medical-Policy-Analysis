import streamlit as st
import langchain_helper1 as lch
from langchain_helper1 import medical_cond_analysis
from langchain_helper1 import split_pdf_into_batches
import boto3
from openai import OpenAI
import boto3
import openai
import streamlit as st
import retrying
import PyPDF2
import boto3
import io
from openai import OpenAI
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

# Load environment variables
load_dotenv()

# Get OpenAI API Key from environment variable
openai_api_key = os.getenv("NA")

if not openai_api_key:
    st.error("OpenAI API key not found. Please set it in your environment variables.")
    st.stop()

st.title("Medical Condition Analysis")

medical_condition = st.sidebar.text_area("Enter the Medical Condition", max_chars=30)

if medical_condition:
    bucket_name = 'policydocumentschiesta'
    common_string = medical_condition  # Specify the common string in file names
    batch_size = 4000

    for text_batch in split_pdf_into_batches(bucket_name, common_string, batch_size):
        response = medical_cond_analysis(medical_condition, text_batch, openai_api_key)
        st.text(response['policy_analysis'])
