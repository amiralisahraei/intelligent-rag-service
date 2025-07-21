# Automated RAG and LLM Fine-Tuning

This project provides an end-to-end pipeline for **automated Retrieval-Augmented Generation (RAG) and Large Language Model (LLM) fine-tuning**, deployment, and serving using AWS SageMaker, FastAPI, and Kubernetes. It enables you to fine-tune LLMs on custom datasets, deploy them as scalable endpoints, and build a retrieval-augmented chatbot application.

## Features

- **Automated LLM Fine-Tuning:** Fine-tune Hugging Face models on your own datasets using SageMaker
- **RAG Pipeline:** Integrate document retrieval with LLMs for context-aware question answering
- **FastAPI Backend:** Serve your chatbot with a modern, async API with JWT authentication support
- **Kubernetes Deployment:** Easily deploy and scale your FastAPI app on EKS
- **CI/CD with GitHub Actions:** Automated workflow for training, deployment, and rolling updates
- **Secure Secrets Management:** Endpoint names and credentials are managed via Kubernetes secrets
- **JWT Authentication:** Secure API endpoints with JSON Web Token authentication

## Project Structure

```
intelligent_rag_system/
│
├── sagemaker/
│   ├── train.py                 # Fine-tuning script for SageMaker
│   └── launch_training.py       # Launches training and deployment on SageMaker
│
├── src/
│   ├── app.py                   # FastAPI application
│   ├── utils.py                 # Utility functions (PDF parsing, vectorstore, LLM calls)
│   └── test.py                  # Simple test script
│
├── kubernetes/
│   ├── deployment.yaml          # K8s deployment manifest
│   └── service.yaml             # K8s service manifest
│
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image for FastAPI app
└── .github/workflows/
    └── example.yml              # GitHub Actions workflow
```

## Prerequisites

- AWS account with SageMaker, ECR, and EKS permissions
- Docker installed locally
- Python 3.12+ environment
- kubectl & AWS CLI configured
- Kubernetes cluster (EKS) set up

## Quick Start

### 1. Fine-Tune and Deploy LLM on SageMaker

Edit your dataset and model parameters in `sagemeker/train.py` as needed.

Launch training and deployment (automated in CI/CD, or manually):

```bash
python launch_training.py
```

This will:
- Fine-tune the model on your dataset
- Deploy the model as a SageMaker endpoint
- Output the endpoint name to `endpoint_name.txt`

### 2. Build and Push the FastAPI Docker Image

```bash
# Build the Docker image
docker build -t fastapi-app-new-image .

# Tag for ECR
docker tag fastapi-app-new-image:latest <your-aws-account-id>.dkr.ecr.<region>.amazonaws.com/fastapi-app-repo:latest

# Push to ECR
docker push <your-aws-account-id>.dkr.ecr.<region>.amazonaws.com/fastapi-app-repo:latest
```

### 3. Deploy to Kubernetes (EKS)

Update your kubeconfig and apply manifests:

```bash
# Configure kubectl for your EKS cluster
aws eks update-kubeconfig --region <region> --name <cluster-name>

# Deploy the application
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### 4. Access the Chatbot API

The FastAPI app exposes a `/llm` endpoint for question answering. The API supports JWT authentication for secure access.

#### Without Authentication (if JWT is disabled):
```bash
curl -X POST "http://<service-endpoint>/llm" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Amirali'\''s email address?"}'
```

#### With JWT Authentication:
```bash
# First, obtain a JWT token (implementation-specific)
TOKEN="your-jwt-token-here"

curl -X POST "http://<service-endpoint>/llm" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question": "What is Amirali'\''s email address?"}'
```

## API Endpoints

### POST /llm
Submit a question to the RAG-enabled chatbot. Supports JWT authentication.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <jwt-token>  # Optional, if JWT auth is enabled
```

**Request Body:**
```json
{
  "question": "Your question here"
}
```

**Response:**
```json
{
  "answer": "Generated response based on retrieved context",
  "status": "success"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Could not validate credentials"
}
```

## Authentication

### JWT Token Support
The API supports JWT (JSON Web Token) authentication for secure access to endpoints. When JWT authentication is enabled:

- Include the `Authorization: Bearer <token>` header in all API requests
- Tokens should be obtained through your authentication system
- Invalid or expired tokens will return a 401 Unauthorized response
- JWT secret key and algorithm can be configured via environment variables

### Configuration
Set the following environment variables to configure JWT authentication:

```bash
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## CI/CD Workflow

The GitHub Actions workflow (`.github/workflows/example.yml`) automates:

1. Code checkout and dependency installation
2. LLM training and deployment on SageMaker
3. Extraction and propagation of the SageMaker endpoint name
4. Docker image build and push to ECR
5. Kubernetes deployment and secret management

## Environment Variables & Secrets

- **ENDPOINT_NAME:** Set automatically from SageMaker deployment and injected into the FastAPI app via Kubernetes secret
- **JWT_SECRET_KEY:** Secret key for JWT token signing and verification
- **JWT_ALGORITHM:** Algorithm used for JWT encoding/decoding (default: HS256)
- **JWT_ACCESS_TOKEN_EXPIRE_MINUTES:** Token expiration time in minutes
- **AWS Credentials:** Managed via GitHub Actions secrets for secure access to AWS services

## Customization

### Dataset Configuration
Update the dataset path and preprocessing logic in `sagemeker/train.py` to work with your specific data format.

### Model Selection
Change the Hugging Face model identifier in `sagemeker/train.py` to use different base models for fine-tuning.

### Prompting & Retrieval
Customize prompt templates and retrieval logic in `src/utils.py` to optimize for your use case and document types.

### Kubernetes Configuration
Modify `kubernetes/deployment.yaml` and `kubernetes/service.yaml` to adjust resource limits, replica counts, and service configuration.

### Authentication Configuration
Customize JWT settings in `src/app.py` to integrate with your existing authentication system or modify token validation logic.

## Troubleshooting

### Common Issues

**SageMaker Training Fails:**
- Check AWS permissions and quotas
- Verify dataset format and S3 bucket access
- Review CloudWatch logs for detailed error messages

**Kubernetes Deployment Issues:**
- Ensure ECR repository permissions are correctly set
- Verify cluster autoscaling is enabled for resource demands
- Check pod logs: `kubectl logs -f deployment/fastapi-app`

**API Connection Problems:**
- Verify service endpoints with: `kubectl get services`
- Check if load balancer is properly configured
- Test internal connectivity first before external access

**JWT Authentication Issues:**
- Verify JWT_SECRET_KEY is properly set in environment variables
- Check token expiration and format
- Ensure Authorization header is properly formatted: `Bearer <token>`
- Review FastAPI logs for authentication-related errors

## Performance Optimization

- **Caching:** Implement Redis caching for frequently accessed documents
- **Batch Processing:** Use batch inference for multiple questions
- **Auto-scaling:** Configure horizontal pod autoscaling based on CPU/memory usage
- **Model Optimization:** Consider model quantization for faster inference

## Security Considerations

- All AWS credentials are managed through IAM roles and GitHub secrets
- Kubernetes secrets are used for sensitive configuration
- JWT authentication provides secure API access with token-based authorization
- Consider implementing API rate limiting and additional authentication layers
- Regular security updates for dependencies
- Rotate JWT secret keys periodically for enhanced security

## License

MIT License - see LICENSE file for details