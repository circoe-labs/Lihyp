FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SIMCO2_DB_PATH=/data/simco2.sqlite \
    SIMCO2_ROUTING_SETTINGS_PATH=/data/routing-settings.json

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN python -m pip install --no-cache-dir . \
    && groupadd --gid 10001 simco2 \
    && useradd --uid 10001 --gid 10001 --system --home-dir /app simco2 \
    && mkdir -p /data \
    && chown -R simco2:simco2 /data

USER 10001:10001
EXPOSE 8000
VOLUME ["/data"]
# Keep ONE worker when using the bundled SQLite database.
CMD ["python", "-m", "uvicorn", "simco2.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
