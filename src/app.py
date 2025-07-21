"""
FastAPI application for resume-based Q&A with authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import boto3
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from requests_aws4auth import AWS4Auth

from src.utils import (
    build_prompt,
    create_vectorstore,
    extract_text_from_pdf,
    llm,
    retrieve_context,
    split_text,
)

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    SECRET_KEY: str = "your-secret-key"  # Should be moved to environment variables
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PDF_PATH: str = "Amirali_Sahraei_CV_OLD.pdf"
    BUCKET_NAME: str = "amirkhan-sh-resume-bucket"
    REGION: str = "us-east-1"
    SERVICE: str = "sagemaker"
    ENDPOINT_NAME: str = os.getenv("ENDPOINT_NAME", "")


class QuestionRequest(BaseModel):
    """Request model for LLM questions."""
    
    question: str


class TokenResponse(BaseModel):
    """Response model for authentication token."""
    
    access_token: str
    token_type: str


class AuthenticationError(HTTPException):
    """Custom authentication error."""
    
    def __init__(self, detail: str = "Invalid authentication credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class AWSService:
    """Handles AWS authentication and configuration."""
    
    def __init__(self, region: str, service: str):
        self.region = region
        self.service = service
        self._session = boto3.Session()
        self._credentials = self._session.get_credentials().get_frozen_credentials()
        
    @property
    def auth(self) -> AWS4Auth:
        """Get AWS4Auth instance."""
        return AWS4Auth(
            self._credentials.access_key,
            self._credentials.secret_key,
            self.region,
            self.service,
            session_token=self._credentials.token,
        )
    
    def get_sagemaker_url(self, endpoint_name: str) -> str:
        """Get SageMaker endpoint URL."""
        return f"https://runtime.sagemaker.{self.region}.amazonaws.com/endpoints/{endpoint_name}/invocations"


class AuthService:
    """Handles authentication operations."""
    
    def __init__(self, secret_key: str, algorithm: str, token_expire_minutes: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=self.token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            raise AuthenticationError()
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user credentials. In production, this should check against a database."""
        return username == "user" and password == "password"


class ResumeProcessor:
    """Handles resume processing and vectorstore operations."""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self._vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize vectorstore with resume data."""
        resume_text = extract_text_from_pdf(self.pdf_path)
        text_chunks = split_text(resume_text)
        self._vectorstore = create_vectorstore(text_chunks)
    
    def get_context(self, question: str) -> str:
        """Retrieve relevant context for a question."""
        if not self._vectorstore:
            raise RuntimeError("Vectorstore not initialized")
        return retrieve_context(question, self._vectorstore)


# Initialize services
config = Config()
aws_service = AWSService(config.REGION, config.SERVICE)
auth_service = AuthService(
    config.SECRET_KEY,
    config.ALGORITHM,
    config.ACCESS_TOKEN_EXPIRE_MINUTES,
)
resume_processor = ResumeProcessor(config.PDF_PATH)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPI app
app = FastAPI(
    title="Resume Q&A API",
    description="API for answering questions about resume content",
    version="1.0.0",
)

# Request headers for SageMaker
SAGEMAKER_HEADERS = {"Content-Type": "application/json"}


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency to get current authenticated user."""
    return auth_service.verify_token(token)


@app.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token."""
    if not auth_service.authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    
    access_token = auth_service.create_access_token(data={"sub": form_data.username})
    return TokenResponse(access_token=access_token, token_type="bearer")


@app.post("/llm")
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Get LLM response for a question about the resume."""
    try:
        context = resume_processor.get_context(request.question)
        prompt = build_prompt(context, request.question)
        
        sagemaker_url = aws_service.get_sagemaker_url(config.ENDPOINT_NAME)
        response = llm(prompt, sagemaker_url, aws_service.auth, SAGEMAKER_HEADERS)
        
        return {"response": response, "context_used": context}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


