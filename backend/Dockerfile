FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY avg-ca.crt* /usr/local/share/ca-certificates/
RUN update-ca-certificates || true

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8420

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8420"]
