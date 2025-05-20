FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["locust", "-f", "main.py", "--host", "http://api:8000", "--web-host", "0.0.0.0"]

