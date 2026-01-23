
# Force rebuild - v2
FROM python:3.12
WORKDIR /usr/local/dzfellah

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs staticfiles media

# Collect static files (for production)
RUN python manage.py collectstatic --noinput || true

# Expose port (Railway will set PORT env variable)
EXPOSE 8000

# Production command with gunicorn
# Change the CMD to this:
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile -"]
