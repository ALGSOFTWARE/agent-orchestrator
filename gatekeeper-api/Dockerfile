# Gatekeeper API Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/

# Create non-root user
RUN useradd -m -u 1000 gatekeeper && chown -R gatekeeper:gatekeeper /app
USER gatekeeper

# Environment variables
ENV PYTHONPATH=/app
ENV MONGODB_URL=mongodb://localhost:27017
ENV DATABASE_NAME=mit_logistics
ENV CREWAI_BASE_URL=http://localhost:8000

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8001/health', timeout=5)"

# Start application
CMD ["python", "-m", "app.main"]