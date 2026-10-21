FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/exports \
    && chown appuser:appuser /app/exports

ENV HOME=/home/appuser
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV UV_NO_SYNC=1

USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
