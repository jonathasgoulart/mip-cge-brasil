# Dockerfile for Unified Deployment
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend and data
COPY api ./api
COPY data ./data
COPY output ./output

# Expose port and start
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
