# Manual App Validation

## Fecha

2026-07-14

## Objetivo

Validar manualmente que la aplicacion funciona de punta a punta con frontend, backend, modelo Champion y flujo de feedback.

Esta validacion no evalua el acabado visual definitivo de UX/UI. Su objetivo es confirmar que la demo integrada funciona como producto: carga datos reales, consulta el modelo, muestra una prediccion y permite registrar aprendizaje operativo.

## Alcance validado

- Frontend React + Vite.
- Backend FastAPI.
- Modelo Champion Random Forest.
- Contrato principal `POST /predict`.
- Endpoint de disponibilidad `GET /health`.
- Endpoint de metadatos `GET /model/info`.
- Endpoint de reservas reales de demo `GET /reservations/demo`.
- Endpoint de feedback `POST /feedback`.
- Endpoint de resumen de feedback `GET /feedback/summary`.

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

## Evidencia documental

- Contrato API: `docs/api_contract.md`.
- Modelo servido por API: `models/champion/random_forest_champion.pkl`.
- Metadatos Champion: `models/champion/champion_metadata.json`.
- Informe tecnico: `reports/model_report.md`.
- Tests automatizados: `tests/`.
- Estado de tareas: `.specify/4_tasks.md`.

## Pendiente fuera de esta validacion

- Mejoras visuales y de UX/UI del frontend.
- Preparacion de capturas finales para presentacion.
- Despliegue web si se aborda el Nivel Avanzado completo.
