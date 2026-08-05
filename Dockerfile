# ═══════════════════════════════════════════════════════
# HiddenYatra — Production Dockerfile
# Multi-stage build for minimal image size
# ═══════════════════════════════════════════════════════

FROM python:3.13-slim AS base

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System dependencies for Pillow and MySQL client
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libjpeg62-turbo-dev \
        libwebp-dev \
        zlib1g-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ── App Setup ──
WORKDIR /app

# Install Python dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directories with correct permissions
RUN mkdir -p \
    static/uploads/places \
    static/uploads/submissions \
    static/uploads/auth \
    static/uploads/hero \
    static/uploads/districts \
    && chmod -R 755 static/uploads

# Create non-root user for security
RUN groupadd -r hiddenyatra && \
    useradd -r -g hiddenyatra -d /app -s /sbin/nologin hiddenyatra && \
    chown -R hiddenyatra:hiddenyatra /app

USER hiddenyatra

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

EXPOSE 5000

# Production server
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
