# Automated RAG & LLM Fine-tuning System

A comprehensive Retrieval-Augmented Generation (RAG) system with LLM fine-tuning capabilities, built with FastAPI and integrated with AWS SageMaker for scalable machine learning inference.

## 🚀 Features

- **Document Processing**: Automated PDF text extraction and chunking
- **Vector Database**: Efficient semantic search using vector embeddings
- **RAG Pipeline**: Context-aware question answering system
- **AWS Integration**: SageMaker endpoint integration for LLM inference
- **Cloud Storage**: S3 integration for document and data storage
- **REST API**: FastAPI-based web service for easy integration
- **Authentication**: AWS4Auth for secure API access

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [AWS Setup](#aws-setup)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- AWS Account with appropriate permissions
- SageMaker endpoint deployed with a language model

### Setup

1. **Clone the repository:**
```bash
git clone <repository-url>
cd rag-llm-system
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install required packages:**
```bash
pip install fastapi uvicorn groq python-dotenv requests requests-aws4auth boto3
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# SageMaker Configuration
SAGEMAKER_ENDPOINT_NAME=huggingface-pytorch-inference-2025-07-13-15-08-32-113
SAGEMAKER_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=amirkhan-sh-resume-bucket

# Application Configuration
PDF_PATH=Amirali_Sahraei_CV_OLD.pdf
```

### File Structure

```
project/
├── main.py              # FastAPI application
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── Amirali_Sahraei_CV_OLD.pdf  # Sample PDF document
└── README.md           # This file
```

## 🚀 Usage

### Starting the Application

1. **Run the FastAPI server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the API:**
   - API Base URL: `http://localhost:8000`
   - Interactive Documentation: `http://localhost:8000/docs`
   - OpenAPI Schema: `http://localhost:8000/openapi.json`

### Making API Requests

**Question Answering:**
```bash
curl -X POST "http://localhost:8000/llm" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the candidate's experience with machine learning?"}'
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/llm",
    json={"question": "What programming languages does the candidate know?"}
)
print(response.json())
```

## 📚 API Documentation

### Endpoints

#### POST `/llm`
Process a question using RAG pipeline and return LLM response.

**Request Body:**
```json
{
  "question": "string"
}
```

**Response:**
```json
{
  "answer": "string",
  "context": "string",
  "confidence": "float"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/llm" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the candidate'\''s educational background?"}'
```

## 🏗️ Architecture

### System Components

1. **Document Processing Pipeline**
   - PDF text extraction
   - Text chunking and preprocessing
   - Vector embedding generation

2. **Vector Database**
   - Semantic search capabilities
   - Context retrieval system
   - Similarity matching

3. **RAG Pipeline**
   - Context-aware prompt building
   - Query processing
   - Response generation

4. **AWS Integration**
   - SageMaker endpoint for LLM inference
   - S3 for document storage
   - AWS4Auth for authentication

### Data Flow

```
PDF Document → Text Extraction → Text Chunking → Vector Store
                                                       ↓
User Question → Context Retrieval → Prompt Building → LLM Inference → Response
```

## ☁️ AWS Setup

### SageMaker Endpoint

1. **Deploy a model to SageMaker:**
```python
import boto3
sagemaker = boto3.client('sagemaker')

# Deploy your model endpoint
# Replace with your model configuration
```

2. **Update endpoint configuration:**
```python
endpoint_name = 'your-endpoint-name'
url = f"https://runtime.sagemaker.{region}.amazonaws.com/endpoints/{endpoint_name}/invocations"
```

### S3 Bucket Setup

1. **Create S3 bucket:**
```bash
aws s3 mb s3://your-bucket-name
```

2. **Configure bucket permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::ACCOUNT-ID:root"
            },
            "Action": "s3:*",
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### IAM Permissions

Required permissions for the application:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sagemaker:InvokeEndpoint",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "*"
        }
    ]
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the web framework
- AWS SageMaker for ML model hosting
- Groq for LLM capabilities
- Community contributors and maintainers

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

---

**Note**: This system is designed for educational and development purposes. For production use, implement additional security measures, error handling, and monitoring capabilities.