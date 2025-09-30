# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /Web

# Install system dependencies (optional: psycopg2, sqlite, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (rename your folder: finance_tracker_web)
COPY finance_tracker_web/ /Web/

# Expose port (Render expects 10000+ but Flask defaults to 5000)
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]
