FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (Docker caches this layer, so rebuilds are fast)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the pipeline code
COPY src/ src/
ENV PYTHONPATH=/app/src

# Running the container runs the pipeline; a date can be passed as an argument
ENTRYPOINT ["python", "-m", "carbon_etl.pipeline"]