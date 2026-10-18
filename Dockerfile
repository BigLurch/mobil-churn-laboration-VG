FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

COPY data/ ./data/
COPY outputs/modell.joblib ./outputs/modell.joblib

CMD ["python", "-m", "churn.score"]