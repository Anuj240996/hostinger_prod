# EasyPanel-safe root Dockerfile for hostinger_prod / version-3.
# Use this when Build Path is the repository root (empty / ".").
# Preferred: set EasyPanel Build Path / Context to DBSolar_19_09_2023
# (that folder already has its own Dockerfile).

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    zbar-tools \
    libzbar0 \
    libcairo2-dev \
    pkg-config \
    bash \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY DBSolar_19_09_2023/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn psycopg2-binary

COPY DBSolar_19_09_2023/ /app/

RUN mkdir -p /app/asert /app/static /app/staticfiles /app/media

ENV DJANGO_SETTINGS_MODULE=inventoryproject.settings
RUN SECRET_KEY=build-collectstatic-only DEBUG=False \
    python manage.py collectstatic --noinput

RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENV WEB_CONCURRENCY=1

# Run via /bin/sh so Docker never execs the script as a binary (avoids
# "exec format error" from CRLF shebang or missing /bin/bash on slim).
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:8000 --workers ${WEB_CONCURRENCY:-1} --timeout 120 --access-logfile - --error-logfile - inventoryproject.wsgi:application"]
