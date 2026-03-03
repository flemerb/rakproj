FROM python:3.11-slim
WORKDIR /app
RUN pip install flask flask-cors
COPY services/auth_service/app.py /app/app.py
RUN mkdir -p /app/data
EXPOSE 5004
CMD ["python", "app.py"]
