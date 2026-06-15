FROM python:3.12-slim

WORKDIR /app

# Install basic compile dependencies for libraries and download OTel Collector
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    && wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.95.0/otelcol-contrib_0.95.0_linux_amd64.tar.gz \
    && tar -zxvf otelcol-contrib_0.95.0_linux_amd64.tar.gz \
    && mv otelcol-contrib /usr/local/bin/otelcol-contrib \
    && rm otelcol-contrib_0.95.0_linux_amd64.tar.gz \
    && apt-get purge -y wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file to leverage Docker layer caching
COPY requirements.txt .

# Install CPU-only PyTorch and requirements to keep the image slim
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and config into the container
COPY app/ ./app/
COPY otel-collector-config.yaml .
COPY start.sh .

# Make the start script executable
RUN chmod +x start.sh

# Create logs directory
RUN mkdir -p logs

# Expose ports for local (8000) and Hugging Face Spaces (7860)
EXPOSE 8000 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application using our entrypoint script
CMD ["/bin/sh", "start.sh"]
