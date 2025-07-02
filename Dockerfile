FROM base-image-langchain-torch-huggingface-fastapi:latest

WORKDIR  /app

COPY app.py utils.py requirements.txt Amirali_Sahraei_CV_OLD.pdf ./

# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

CMD ["fastapi", "run", "app.py", "--host", "0.0.0", "--port", "8000"]