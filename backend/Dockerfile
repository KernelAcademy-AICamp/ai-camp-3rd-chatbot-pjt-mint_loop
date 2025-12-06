# Trip Kit Backend - API Server & LangGraph Agents
#
# Agents:
#   - RecommendationAgent: 여행지 추천 (Gemini 2.5 Pro)
#   - ImageGenerationAgent: 이미지 생성 (Gemini Imagen 3.0)

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for logs, data, and credentials
RUN mkdir -p /app/logs /app/data /app/credentials

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Note: Application environment variables are set via docker-compose.yml
# from root .env file (GEMINI_TEXT_MODEL, GEMINI_IMAGE_MODEL, VERTEX_PROJECT_ID, etc.)

# Expose port for API server
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command: Run API server
CMD ["python", "-m", "src.api_server.server"]
