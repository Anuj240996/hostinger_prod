# Python 3.10 (matches production 3.10.20)
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
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

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --force-reinstall python-barcode==0.13.1 pdf417gen==0.8.1 && \
    pip install --no-cache-dir gunicorn psycopg2-binary

# Copy project files (including asert/, media/, and static/ directories)
COPY . /app/

# Ensure directories exist (in case they're empty, mkdir -p won't overwrite existing content)
# staticfiles is where collectstatic will gather all static files
RUN mkdir -p /app/asert /app/static /app/staticfiles /app/media

# Bake static files into the image so the container can start Gunicorn immediately.
ENV DJANGO_SETTINGS_MODULE=inventoryproject.settings
RUN SECRET_KEY=build-collectstatic-only DEBUG=False \
    python manage.py collectstatic --noinput

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port (map host 8001→8000 in EasyPanel if V1 already uses host :8000)
EXPOSE 8000

ENV WEB_CONCURRENCY=1

# Run via /bin/sh so Docker never execs the script as a binary (avoids
# "exec format error" from CRLF shebang or missing /bin/bash on slim).
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

# Default command (1 worker by default — lowers RAM on small VPS)
CMD ["sh", "-c", "exec gunicorn --chdir /app --bind 0.0.0.0:8000 --workers ${WEB_CONCURRENCY:-1} --timeout 120 --access-logfile - --error-logfile - gunicorn_wsgi:application"]
