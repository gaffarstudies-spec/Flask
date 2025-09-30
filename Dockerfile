# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY Finance\ Tracker\ Web/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY Finance\ Tracker\ Web/ /app/

# Expose port
EXPOSE 8000

# Run the app with gunicorn
CMD ["gunicorn", "Web:app", "--bind", "0.0.0.0:8000"]
