FROM python:3.12-slim

RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/sh --create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what the service needs
COPY l4/ l4/
COPY data/ data/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8766

CMD ["sh", "-c", "uvicorn l4.registry.api.app:app --host 0.0.0.0 --port ${PORT:-8766}"]
