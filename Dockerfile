
# Python runtime for the enterprise API.
FROM python:3.13-slim

# Prevent Python from writing bytecode and buffer-free logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install only the API runtime dependencies.
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy only the application components required by the API.
COPY main.py config.py ./
COPY pipelines/ ./pipelines/
COPY security/ ./security/
COPY app/ ./app/

# Run the API as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# Document the container's internal application port.
EXPOSE 8000

# Start the FastAPI application.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
