import boto3
import openai
import streamlit as st
# import pdb
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

from dotenv import load_dotenv

load_dotenv()

def medical_cond_analysis(medical_condition):
    llm = OpenAI(temperature=0.7, openai_api_key= 'NA' )

    prompt_template_name = PromptTemplate(
        input_variables=['medical_condition'],
        template="I am a Hospital Medical Policy Analyst {medical_condition}. The {medical_condition} is for a patient. Please Analyze the documents and provide a comparative analysis in tabular format for different Insurance Providers considering fields"
    )

    # pdb.set_trace()
    name_chain = LLMChain(llm=llm, prompt=prompt_template_name, output_key="policy_analysis")

    response = name_chain({'medical_condition': medical_condition})

    return response


if __name__ == '__main__':
    print(medical_cond_analysis('Cochlear Implantation'))
