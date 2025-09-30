# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements first (for better caching)
COPY web/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY web/ /app/

# Expose Flask default port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
