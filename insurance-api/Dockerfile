FROM python:3.13-slim

WORKDIR /app

# Install deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed the catalogue on build so the container starts ready.
# For Postgres the seed runs at startup instead (see entrypoint.sh).
EXPOSE 8001

CMD ["sh", "-c", "python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8001"]