FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/
COPY services/prediction_service/app.py /app/app.py

# Create necessary directories
RUN mkdir -p /app/models

EXPOSE 5003

CMD ["python", "app.py"]
