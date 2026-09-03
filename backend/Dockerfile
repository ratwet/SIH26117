# =====================================================================
# SovereignWorkbench — Central GPU Server Container (Dockerfile)
# Multi-stage lightweight image with bubblewrap namespace support
# =====================================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install bubblewrap for isolated sandbox execution and basic system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    bubblewrap \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY app/ ./app/

# Create persistent storage directories
RUN mkdir -p /app/data/uploads /app/data/deliverables /app/data/chromadb /app/models_storage

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Launch production ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
