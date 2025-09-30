FROM python:3.10-slim

WORKDIR /app

# Copy requirements first and install
COPY Web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY Web/ /app/

EXPOSE 5000

# Start your app
CMD ["python", "Web.py"]
