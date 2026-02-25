# ---- Build stage ----
FROM mcr.microsoft.com/devcontainers/python:3.12 AS builder

WORKDIR /app

# Installeer dependencies in een virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage ----
FROM mcr.microsoft.com/devcontainers/python:3.12

WORKDIR /app

# Kopieer venv van builder
COPY --from=builder /opt/venv /opt/venv

# Kopieer broncode
COPY app/ ./app/

# Gebruik de venv
ENV PATH="/opt/venv/bin:$PATH"

# Non-root gebruiker
USER vscode

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
