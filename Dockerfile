
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proxy server code
COPY main.py .

# Expose port 
EXPOSE 8080

CMD ["python", "main.py"]
