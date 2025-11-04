# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--app-dir", "src"]
