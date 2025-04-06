FROM python:3.9-slim

# Install PostgreSQL client and build dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /usr/src/app/

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "run:app"]