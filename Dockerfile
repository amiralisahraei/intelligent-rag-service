FROM amiralisahraei/base-image:latest

WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY . .

# Install dependencies
# RUN pip install --upgrade pip
# RUN pip install --no-cache-dir -r requirements.txt


# Expose the port   
EXPOSE 8000

# Run the application using Uvicorn
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]