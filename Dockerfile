FROM python:3.11-slim

# Set environment variables:
# 1. Do not cache bytecode.
# 2. Force stdout and stderr to not be buffered.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy only poetry dependency files first to utilize Docker build layer caching
COPY pyproject.toml poetry.lock* /app/

# Disable virtualenv creation because Docker acts essentially as a virtual environment
RUN poetry config virtualenvs.create false \
    # Install project dependencies without development packages initially
    && poetry install --no-interaction --no-ansi

# Copy project files
COPY . /app/

# Expose the Flask port
EXPOSE 5000

# Default command (overridden via docker-compose for dev)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
