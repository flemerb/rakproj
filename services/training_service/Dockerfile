FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/
COPY services/training_service/app.py /app/app.py

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/preprocessed /app/models /app/mlruns

EXPOSE 5002

CMD ["python", "app.py"]
