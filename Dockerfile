FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 seti && chown -R seti:seti /app
USER seti

# Expose port
EXPOSE $PORT

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "--timeout", "120", "run:app"]

