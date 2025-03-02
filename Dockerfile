# Use Python 3.10 as the base image
FROM python:3.10

# Set the application home directory
ENV APP_HOME=/app
WORKDIR $APP_HOME

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip is up-to-date
RUN pip install --no-cache-dir --upgrade pip

# Create virtual environment explicitly
RUN python -m venv /app/.venv

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Copy requirements first to leverage Docker caching
COPY requirements.txt $APP_HOME/requirements.txt

# Activate virtual environment and install dependencies
RUN /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose FastAPI's default port
EXPOSE 8000

# Run the application using the virtual environment
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
