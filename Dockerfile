FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any needed for numpy/etc)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app
