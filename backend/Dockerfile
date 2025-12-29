FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create directory for ChromaDB persistence
RUN mkdir -p /app/chroma_db

# Set environment variables
ENV PORT=8080
ENV CHROMA_PERSIST_DIR=/app/chroma_db

# Run the application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}