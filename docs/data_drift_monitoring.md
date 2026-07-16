# Data Drift Monitoring

## Objetivo

Detectar cambios en la distribucion de las variables recibidas por el modelo antes de que esos cambios degraden silenciosamente la calidad de las predicciones.

El monitor genera una senal para revision. No reentrena, reemplaza ni promociona modelos automaticamente.

## Estado de implementacion

La implementacion tecnica esta completa: perfil de referencia versionado, ingesta desde `prediction_logs`, filtrado por origen, calculo PSI, contrato API y tests automatizados. En un entorno con menos de 100 predicciones operativas reales, `insufficient_data` es el resultado correcto y no indica una funcionalidad incompleta.

## Fuente de referencia

El perfil de referencia se genera con el split de entrenamiento estratificado usado por el proyecto:

```text
models/monitoring/training_reference_profile.json
```

El perfil incluye version, hash del dataset, contrato del split, numero de filas, umbrales y distribuciones por variable. El holdout final no se utiliza para construir esta referencia.

## Datos actuales

La muestra procede de `prediction_logs`, que contiene todas las respuestas correctas de `POST /predict` en SQLite o PostgreSQL. El resultado real de la reserva puede seguir siendo desconocido porque el data drift solo necesita variables de entrada.

Para evitar que el CSV historico de demostracion contamine una muestra supuestamente productiva, cada inferencia registra su origen:

- `frontend_manual`: calculo solicitado por una persona desde la evaluacion de reserva.
- `frontend_demo_queue`: calculo automatico de las reservas historicas mostradas en la cola.
- `api`: llamada externa sin un origen frontend especifico.

El monitor utiliza las 1.000 predicciones operativas mas recientes. Excluye `frontend_demo_queue` y el origen heredado `prediction_api`, utilizado antes de que la API distinguiera el tipo de trafico. Todas las predicciones permanecen disponibles en auditoria aunque no formen parte del calculo PSI.

## Metodo y umbrales

Se utiliza Population Stability Index (PSI):

- Variables numericas: intervalos definidos por deciles del entrenamiento.
- Variables categoricas y binarias: distribucion de frecuencias, con control de categorias no vistas.
- PSI menor de `0.10`: estable.
- PSI entre `0.10` y `0.25`: drift moderado.
- PSI igual o superior a `0.25`: drift alto.

El calculo requiere al menos 100 registros actuales validos. Con una muestra menor el sistema devuelve `insufficient_data` y no calcula una alerta concluyente.

## Endpoint

```text
GET /monitoring/drift
```

Estados posibles:

- `insufficient_data`: no existe una muestra minima fiable.
- `stable`: no se supera el umbral moderado.
- `warning`: una o mas variables muestran drift moderado.
- `drift_detected`: una o mas variables muestran drift alto.

La respuesta contiene `data_source`, limite de muestra, fuentes excluidas, PSI maximo, variables alertadas y detalle por variable cuando la muestra es suficiente.

## Dashboard

El estado operativo tambien puede consultarse en una entrada web separada de la aplicacion de negocio:

```text
Local:      http://localhost:5173/monitoring
Desplegado: https://d3lxpalnzir74p.cloudfront.net/monitoring
```

El dashboard consulta `GET /health/ready`, `GET /model/info`, `GET /feedback/summary` y `GET /monitoring/drift`. No fabrica metricas: mientras no existan 100 predicciones operativas validas muestra `Muestra insuficiente` y el progreso real de la muestra.

La vista incluye modulos reservados para red neuronal, A/B Testing y promocion condicionada. Permanecen como `Pendiente de evaluacion` hasta que exista evidencia reproducible; el dashboard no enlaza desde la navegacion comercial ni modifica su flujo.

## Operacion

Regenerar el perfil solo si cambia de forma aprobada el dataset, el contrato de variables o el split de entrenamiento:

```bash
python -m src.mlops.data_drift
```

Ejecutar las verificaciones:

```bash
python -m pytest tests/unit/test_data_drift.py tests/unit/test_prediction_ingestion.py tests/test_backend_api.py
```

## Regla de decision

Una alerta de drift abre una revision de datos y rendimiento. Para promover otro modelo siguen siendo obligatorias las reglas de metricas, overfitting, versionado, tests y aprobacion del equipo.
