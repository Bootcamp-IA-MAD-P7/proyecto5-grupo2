# Observabilidad operativa

## Objetivo

Hotel Insights aplica una observabilidad proporcionada al alcance del proyecto: permite distinguir disponibilidad, dependencias y errores de solicitud sin introducir una plataforma externa de metricas.

## Health checks

- `GET /health`: liveness. Confirma que el proceso FastAPI responde.
- `GET /health/ready`: readiness. Comprueba que el Champion se puede cargar y que existen las tablas operativas `prediction_logs` y `prediction_feedback`.
- Docker y `scripts/deploy_ec2.sh` usan readiness para no publicar una API sin sus dependencias.
- Readiness responde `200` cuando el servicio esta preparado y `503` cuando alguna dependencia falla.
- Una base accesible pero sin las migraciones Alembic requeridas se considera `not_ready`.

## Correlacion

Todas las respuestas incluyen la cabecera `X-Request-ID`.

- Se conserva el valor aportado por el cliente si contiene solo caracteres seguros y no supera 128 caracteres.
- Se genera un UUID cuando falta o no es valido.
- El mismo identificador aparece en los logs de solicitud y de prediccion.
- Una prediccion correcta relaciona `request_id` con el `prediction_id` persistido en `prediction_logs`.

## Logs estructurados

FastAPI escribe eventos JSON en la salida estandar del contenedor:

- `request_completed`: metodo, ruta, status y duracion.
- `request_failed`: metodo, ruta, duracion y tipo de excepcion.
- `prediction_completed`: `request_id`, `prediction_id`, version, origen y nivel de riesgo.

No se registran payloads de reserva, credenciales, contraseñas ni cadenas de conexion.

## Consulta en Docker

```bash
docker compose logs backend --tail=100
```

En EC2:

```bash
docker compose --env-file .env.ec2 -f docker-compose.ec2.yml logs backend --tail=100
```

## Panel interno

La ruta independiente `/monitoring` reúne el estado de readiness, Champion, feedback, Data Drift y experimentos expertos sin entrar en la navegación comercial. Consume:

- `GET /health/ready`.
- `GET /model/info`.
- `GET /feedback/summary`.
- `GET /monitoring/drift`.
- `GET /monitoring/experiments`.

La evidencia de red neuronal, A/B Testing y promoción condicionada procede de artefactos versionados del repositorio. La vista es de solo lectura y no ejecuta entrenamientos, promociones ni cambios de configuración.

## Verificacion

```bash
python -m pytest tests/test_backend_api.py tests/unit/test_observability.py tests/integration/test_prediction_feedback_smoke.py
```

La cobertura comprueba readiness correcto y degradado, propagacion de `X-Request-ID`, correlacion con `prediction_id` y ausencia de payloads en los eventos operativos.
