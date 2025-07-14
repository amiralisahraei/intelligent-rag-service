import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import boto3
import requests
import json


def extract_text_from_pdf(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def split_text(text: str, chunk_size: int = 200) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size)
    return splitter.split_text(text)

def create_vectorstore(chunks: list, model_name: str = "all-MiniLM-L6-v2"):
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    return FAISS.from_texts(chunks, embedding=embeddings)

def retrieve_context(query: str, vectorstore, k: int = 5) -> str:
    docs = vectorstore.similarity_search(query, k=k)
    return "\n".join(d.page_content for d in docs)

def build_prompt(context: str, question: str) -> str:
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are a helpful assistant. Use the provided context to answer the question.\n"
            "Context: {context}\n"
            "Question: {question}\n"
            "Answer:"
        ),
    )
    return prompt.format(context=context, question=question)

def get_llm_response(prompt: str, client) -> str:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    return response

def llm(user_input: str, url: str, awsauth, headers: dict):
    data = {
    "inputs": user_input,
    "parameters": {
        "max_new_tokens": 50,
        "temperature": 0.7,
        "return_full_text": False
    }
    }

    response = requests.post(url, auth=awsauth, json=data, headers=headers)
    return response

def answer_question(question: str, vectorstore, url, awsauth, headers) -> str:
    context = retrieve_context(question, vectorstore)
    prompt = build_prompt(context, question)
    # return get_llm_response(prompt, client)
    return llm(prompt, url, awsauth, headers)


def upload_to_s3(chunks: list, bucket_name: str):
    s3 = boto3.client('s3')
    for i, chunk in enumerate(chunks):
        s3.put_object(
            Bucket=bucket_name,
            Key=f'resume_chunk_{i}.txt',
            Body=chunk.encode('utf-8')
        )
        print(f'Uploaded chunk {i} to S3')





