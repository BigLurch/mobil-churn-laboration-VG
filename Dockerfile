FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV PYTHONPATH=/app/src

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv sync --locked --no-dev --no-editable

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app/src

COPY data/ ./data/
COPY outputs/modell.joblib ./outputs/modell.joblib

CMD ["python", "-m", "churn.score"]