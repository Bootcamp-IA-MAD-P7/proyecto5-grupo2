# Manual App Validation

## Fecha

2026-07-16

## Objetivo

Validar manualmente que la aplicacion funciona de punta a punta con frontend, backend, modelo Champion y flujo de feedback.

Esta validacion confirma tanto el flujo integrado como la coherencia del frontend definitivo: carga datos reales, consulta el modelo, muestra una prediccion, registra aprendizaje operativo y presenta evidencia analitica consistente.

## Alcance validado

- Frontend React + Vite.
- Backend FastAPI.
- Modelo Champion Random Forest.
- Contrato principal `POST /predict`.
- Endpoint de disponibilidad `GET /health`.
- Endpoint de metadatos `GET /model/info`.
- Endpoint de reservas reales de demo `GET /reservations/demo`.
- Paginacion y busqueda determinista de reservas mediante `limit`, `offset` y metadatos de pagina.
- Endpoint de feedback `POST /feedback`.
- Endpoint de resumen de feedback `GET /feedback/summary`.
- Persistencia PostgreSQL en Amazon RDS.
- Despliegue HTTPS mediante CloudFront y EC2.
- Despliegue automático desde `develop` mediante GitHub Actions.
- Dashboard MLOps independiente `/monitoring` y evidencia `GET /monitoring/experiments`.
- Portada visual, navegación de producto y página `Modelo` con evidencia del dataset, EDA, entrenamiento, métricas y limitaciones.

## Flujo funcional revisado

1. El backend se inicia correctamente.
2. El frontend se inicia correctamente.
3. La app carga reservas desde el backend.
4. El usuario puede revisar una reserva.
5. La app solicita una prediccion al endpoint `POST /predict`.
6. El backend responde usando el Champion Random Forest.
7. La respuesta incluye:
   - prediccion,
   - probabilidad,
   - nivel de riesgo,
   - version del modelo.
8. El usuario puede registrar feedback operativo.
9. El backend guarda el feedback.
10. El resumen de feedback queda disponible para monitorizacion basica.

## Resultado

Validacion manual superada.

La aplicacion queda validada funcionalmente como demo integrada: frontend, backend, Champion Random Forest y feedback operan de forma conectada.

La validacion operativa en AWS confirma además:

- Frontend público accesible desde escritorio y móvil.
- `GET /api/health` responde correctamente mediante CloudFront.
- `GET /api/model/info` informa del Champion `random_forest_champion_v0.1.0` cargado.
- `GET /api/feedback/summary` identifica el almacenamiento como `postgresql`.
- Los registros permanecen después de reiniciar el backend.
- La IP directa de EC2 no es accesible por HTTP después de limitar el origen a CloudFront.
- `/monitoring`, `/api/health/ready`, `/api/monitoring/experiments` y la paginacion de reservas responden publicamente con `200 OK`.
- La app principal, `/monitoring`, `/monitoring.html`, `/api/health/ready` y `/api/model/info` responden públicamente con `200 OK` sobre el commit `d752892`.
- La suite final ejecuta 76 tests y el build de frontend transforma 1.605 modulos correctamente.
- Las cifras de la página `Modelo` se contrastaron con el CSV: 36.275 reservas, 32,76% canceladas, medianas de `lead_time` 122/39 y tasas segmentadas coincidentes.
- Las métricas de test mostradas coinciden con `reports/champion_test_metrics.json` y los metadatos del Champion.
- `pip-audit` y `pnpm audit --prod` no detectaron vulnerabilidades conocidas.
- El stack Docker completo queda saludable con Champion y PostgreSQL disponibles.

## Evidencia documental

- Contrato API: `docs/api_contract.md`.
- Modelo servido por API: `models/champion/random_forest_champion.pkl`.
- Metadatos Champion: `models/champion/champion_metadata.json`.
- Informe tecnico: `reports/model_report.md`.
- Tests automatizados: `tests/`.
- Estado de tareas: `.specify/4_tasks.md`.
- Operación AWS: `docs/aws_deployment.md`.

## Pendiente fuera de esta validacion

- Preparacion de capturas finales para presentacion.
- Preparacion de las presentaciones finales.
- Release final de `develop` a `main` y tag `v1.0.0`.
