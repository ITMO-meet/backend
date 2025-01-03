FROM python:3.11-slim

WORKDIR /app

# Build args
ARG MONGO_URI
ARG MINIO_ENDPOINT
ARG MINIO_ACCESS_KEY
ARG MINIO_SECRET_KEY
ARG MINIO_BUCKET_NAME
ARG MINIO_CALENDAR_ACCESS_KEY
ARG MINIO_CALENDAR_SECRET_KEY
ARG MINIO_CALENDAR_BUCKET_NAME
ARG MINIO_USE_SSL
ARG ENVIRONMENT

# ENV variables from build args
ENV MONGO_URI=${MONGO_URI}
ENV MINIO_ENDPOINT=${MINIO_ENDPOINT}
ENV MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
ENV MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
ENV MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME}
ENV MINIO_CALENDAR_ACCESS_KEY=${MINIO_CALENDAR_ACCESS_KEY}
ENV MINIO_CALENDAR_SECRET_KEY=${MINIO_CALENDAR_SECRET_KEY}
ENV MINIO_CALENDAR_BUCKET_NAME=${MINIO_CALENDAR_BUCKET_NAME}
ENV MINIO_USE_SSL=${MINIO_USE_SSL}
ENV ENVIRONMENT=${ENVIRONMENT}

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
