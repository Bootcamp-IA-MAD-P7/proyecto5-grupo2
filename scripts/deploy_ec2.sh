#!/usr/bin/env bash

set -Eeuo pipefail

APP_DIR="${APP_DIR:-/home/ubuntu/hotel-insights}"
COMPOSE_FILE="${APP_DIR}/docker-compose.ec2.yml"
ENV_FILE="${APP_DIR}/.env.ec2"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing deployment environment file: ${ENV_FILE}" >&2
  exit 1
fi

cd "${APP_DIR}"

docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" config --quiet
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" up -d --build --remove-orphans

for attempt in $(seq 1 24); do
  if curl --fail --silent --show-error http://localhost/api/health/ready >/dev/null; then
    curl --fail --silent --show-error http://localhost/api/model/info
    echo
    docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps
    docker image prune --force
    exit 0
  fi

  echo "Waiting for the API readiness check (${attempt}/24)..."
  sleep 5
done

echo "Deployment failed: API readiness check did not pass." >&2
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" ps >&2
docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" logs --tail=100 >&2
exit 1
