# Multi-stage build for Flask + React application
FROM node:18-alpine AS frontend-build

# Build React frontend (moved to top-level `frontend`)
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src folder
COPY src/ ./src/

# Copy built React frontend from previous stage: flatten static assets
RUN rm -rf src/static
# Copy index.html
COPY --from=frontend-build /frontend/build/index.html ./src/static/index.html
# Copy JS and CSS bundles
COPY --from=frontend-build /frontend/build/static/js ./src/static/js
COPY --from=frontend-build /frontend/build/static/css ./src/static/css

# Create a non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for Flask app
EXPOSE 5000

# Default command to run Flask app
CMD ["python", "src/app.py"]
