FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL your application code
COPY . .

EXPOSE 5000

CMD ["python", "server.py"]

