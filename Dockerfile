FROM python:3.10-slim

WORKDIR /app

COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web/ /app/

EXPOSE 5000

CMD ["python", "Web.py"]
