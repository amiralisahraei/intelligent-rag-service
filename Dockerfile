# FROM base-image-langchain-torch-huggingface-fastapi:latest
###
FROM python:3.12-slim

# WORKDIR  /app

# COPY . .
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# EXPOSE 8000

# CMD ["fastapi", "run", "app.py", "--host", "0.0.0", "--port", "8000"]