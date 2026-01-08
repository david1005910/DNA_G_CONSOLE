# filename: Dockerfile
# --- STAGE 1: Builder ---
FROM python:3.9-slim AS builder

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Train model
RUN python train_model.py


# --- STAGE 2: Final Production Image ---
FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

# Copy trained model files
COPY --from=builder /app/ml_models /app/ml_models

# Copy application source code
COPY dna_app/ ./dna_app/
COPY config.py .
COPY run.py .
COPY train_model.py .
COPY setup.py .

# Expose port
EXPOSE 5001

# Run server
CMD ["python", "run.py"]
