FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements-backend.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-backend.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app/backend ./app/backend
COPY src ./src
COPY scripts/start_backend.sh ./scripts/start_backend.sh
COPY data/raw ./data/raw
COPY models/champion ./models/champion
COPY models/monitoring ./models/monitoring
COPY reports/neural_network_experiment.json ./reports/neural_network_experiment.json
COPY reports/offline_ab_test_results.json ./reports/offline_ab_test_results.json
COPY reports/conditional_promotion_decision.json ./reports/conditional_promotion_decision.json
RUN chmod +x ./scripts/start_backend.sh

EXPOSE 8000

CMD ["./scripts/start_backend.sh"]
