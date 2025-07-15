from fastapi import FastAPI
from typing import Union
from dotenv import load_dotenv
import os
import boto3
from requests_aws4auth import AWS4Auth

from src.utils import (
    extract_text_from_pdf,
    split_text,
    create_vectorstore,
    retrieve_context,
    build_prompt,
    llm,
    # get_llm_response,  # Remove unused imports
    # upload_to_s3
)

# Load environment variables
load_dotenv()

# Constants
PDF_PATH = "Amirali_Sahraei_CV_OLD.pdf"
BUCKET_NAME = "amirkhan-sh-resume-bucket"
REGION = 'us-east-1'
SERVICE = 'sagemaker'

# AWS authentication setup
session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    SERVICE,
    session_token=credentials.token
)

# SageMaker endpoint setup
endpoint_name = os.getenv('ENDPOINT_NAME')
url = f"https://runtime.sagemaker.{REGION}.amazonaws.com/endpoints/{endpoint_name}/invocations"
headers = {"Content-Type": "application/json"}

# Initialize resources at startup
resume_text = extract_text_from_pdf(PDF_PATH)
text_chunks = split_text(resume_text)
# Optionally upload to S3 if needed
# upload_to_s3(text_chunks, BUCKET_NAME)
vectorstore = create_vectorstore(text_chunks)

app = FastAPI()

@app.post("/llm")
def get_llm_response(question: Union[str, None]):
    context = retrieve_context(question, vectorstore)
    prompt = build_prompt(context, question)
    response = llm(prompt, url, awsauth, headers)
    return response
