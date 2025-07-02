from groq import Groq
from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv

from utils import (
    extract_text_from_pdf,
    split_text,
    create_vectorstore,
    retrieve_context,
    build_prompt,
    get_llm_response,
    upload_to_s3
)

load_dotenv()

PDF_PATH = "Amirali_Sahraei_CV_OLD.pdf"
BUCKET_NAME = "amirkhan-sh-resume-bucket"


# Initialize resources at startup
resume_text = extract_text_from_pdf(PDF_PATH)
text_chunks = split_text(resume_text)

# Upload the text chunks to S3
# upload_to_s3(text_chunks, BUCKET_NAME)

vectorstore = create_vectorstore(text_chunks)
llm_client = Groq()

app = FastAPI()

@app.post("/llm")
def read_root(question: Union[str, None]):
    context = retrieve_context(question, vectorstore)
    prompt = build_prompt(context, question)
    response = get_llm_response(prompt, llm_client)
    return {"response": response}

