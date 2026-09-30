# SAMS Backend Dockerfile
# Build: docker build -t sams-backend ./backend
# Stage 1: Production image (không có dev tools)
FROM python:3.12-slim

# Metadata
LABEL maintainer="SAMS Team"
LABEL description="Smart Apartment Management System - Flask Backend"

# Biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production

# Thư mục làm việc
WORKDIR /app

# Cài thư viện hệ thống cần thiết cho SQLite và image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements trước (tận dụng Docker layer cache)
COPY requirements.txt .

# Cài Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Tạo thư mục cần thiết với đúng permissions
RUN mkdir -p /app/instance /app/uploads /app/logs && \
    chmod 755 /app/instance /app/uploads /app/logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Entrypoint: 1 worker vì SQLite không hỗ trợ multi-process write
# --timeout 120: Đủ thời gian cho các query phức tạp (OCR, AI analysis)
CMD ["gunicorn", \
     "--workers", "1", \
     "--worker-class", "sync", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "run:app"]
