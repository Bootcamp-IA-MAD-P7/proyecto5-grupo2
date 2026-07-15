# Data Drift Monitoring

## Objetivo

Detectar cambios en la distribucion de las variables recibidas por el modelo antes de que esos cambios degraden silenciosamente la calidad de las predicciones.

El monitor genera una senal para revision. No reentrena, reemplaza ni promociona modelos automaticamente.

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
