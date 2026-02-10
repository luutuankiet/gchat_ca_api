# Dockerfile for Cloud Run deployment
# Runs the Flask connector that bridges Google Chat and Vertex AI

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Cloud Run requires the app to listen on $PORT
# Default to 8080 for local testing
ENV PORT=8080

# Run the application with gunicorn
# --bind 0.0.0.0:$PORT - Listen on all interfaces
# --workers 2 - Use 2 worker processes for handling requests
# --timeout 0 - No timeout (CA API queries can take time)
# --worker-class gevent - Use async workers for better performance
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 0 --worker-class gevent app:app
