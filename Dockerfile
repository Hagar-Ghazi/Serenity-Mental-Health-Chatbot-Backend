FROM python:3.10-slim

WORKDIR /app

# Install basic compile dependencies for libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file to leverage Docker layer caching
COPY requirements.txt .

# Install CPU-only PyTorch and requirements to keep the image slim
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code into the container
COPY app/ ./app/

# Create logs directory
RUN mkdir -p logs

# Expose port for the FastAPI server
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
