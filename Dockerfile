FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-local.txt .
RUN pip install --no-cache-dir -r requirements-local.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]