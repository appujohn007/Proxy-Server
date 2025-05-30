
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proxy server code
COPY proxy_server.py .

# Expose port 3130
EXPOSE 3130

CMD ["python", "proxy_server.py"]
