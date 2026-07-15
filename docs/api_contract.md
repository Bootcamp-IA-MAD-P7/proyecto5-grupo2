# API Contract - Hotel Insights

Este contrato define la comunicacion inicial entre la aplicacion web y el backend de prediccion.

Estado: vigente para la API actual con Champion Random Forest. El contrato debe actualizarse si cambia el pipeline final de preprocesamiento o el formato de entrada/salida.

## 1. Objetivo

El frontend debe enviar los datos de una reserva hotelera al backend y recibir una respuesta consistente con:

- Prediccion de cancelacion.
- Probabilidad.
- Nivel de riesgo.
- Version del modelo.
- Factores principales y recomendacion operativa.

## 2. Base URL

AWS:

```text
https://d3lxpalnzir74p.cloudfront.net/api
```

Backend local:

```text
http://localhost:8000
```

El frontend puede configurar esta URL mediante:

```text
VITE_API_URL
```

En Docker y AWS se usa `/api` para que nginx reenvie las solicitudes al backend dentro de la red de contenedores.

Ejecutar backend local desde la raiz del repositorio:

```bash
uvicorn app.backend.main:app --reload
```

## 3. Health Check

### `GET /health`

Comprueba que la API esta disponible.

#### Response `200 OK`

```json
{
  "status": "ok",
  "service": "hotel-insights-api",
  "version": "0.1.0"
}
```

## 4. Model Info

### `GET /model/info`

Devuelve el estado del modelo que usa la API.

Este endpoint informa del modelo que usa la API para generar predicciones.

#### Response `200 OK`

```json
{
  "model_loaded": true,
  "model_version": "random_forest_champion_v0.1.0",
  "model_status": "loaded",
  "model_type": "RandomForestClassifier",
  "primary_metric": "f1_canceled",
  "target": "booking_status",
  "positive_class": "Canceled",
  "notes": [
    "Champion Random Forest pipeline loaded from repository artifact.",
    "The pipeline includes preprocessing and binary cancellation classification.",
    "Champion selection metadata is stored in models/champion/champion_metadata.json."
  ]
}
```

## 5. Reservation Candidates Endpoint

### `GET /reservations/demo`

Devuelve una lista de reservas candidatas obtenidas desde el CSV real del proyecto.

Uso actual:

- Alimentar la tabla de reservas del frontend principal.
- Alimentar el panel de alertas del frontend principal.
- Permitir que la app calcule predicciones reales para reservas reales del dataset.

Query params:

| Parametro | Tipo | Obligatorio | Descripcion |
| --- | --- | --- | --- |
| `limit` | integer | no | Numero maximo de reservas a devolver. Valor usado por defecto: `8`. |

#### Response `200 OK`

```json
{
  "total_available": 36275,
  "returned": 2,
  "source": "data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv",
  "reservations": [
    {
      "id": "INN02825",
      "display_name": "Reserva INN02825",
      "stay_label": "Suite familiar · 7 noches",
      "status_label": "Conviene confirmar",
      "image_key": "terrace",
      "input_data": {
        "lead_time": 279,
        "arrival_year": 2018,
        "arrival_month": 9,
        "arrival_date": 20,
        "no_of_special_requests": 0,
        "avg_price_per_room": 177.3,
        "market_segment_type": "Online",
        "no_of_weekend_nights": 2,
        "no_of_week_nights": 5,
        "type_of_meal_plan": "Meal Plan 1",
        "room_type_reserved": "Room_Type 6",
        "no_of_adults": 2,
        "no_of_children": 2,
        "required_car_parking_space": 0,
        "repeated_guest": 0,
        "no_of_previous_cancellations": 0,
        "no_of_previous_bookings_not_canceled": 0
      }
    }
  ]
}
```

### Reservation Output Fields

| Campo | Tipo | Descripcion |
| --- | --- | --- |
| `total_available` | integer | Numero total de filas disponibles en el CSV real. |
| `returned` | integer | Numero de reservas devueltas en la respuesta. |
| `source` | string | Ruta relativa del dataset usado por el backend. |
| `reservations` | array | Lista de reservas candidatas. |
| `id` | string | Identificador historico de reserva. |
| `display_name` | string | Nombre visible de la reserva en la app. |
| `stay_label` | string | Texto de estancia para la interfaz. |
| `status_label` | string | Etiqueta operativa calculada para priorizacion visual. |
| `image_key` | string | Clave visual usada por el frontend si necesita imagen asociada. |
| `input_data` | object | Payload compatible con `POST /predict`. |

## 6. Prediction Endpoint

### `POST /predict`

Calcula el riesgo de cancelacion de una reserva.

El endpoint acepta un JSON con los campos del formulario y las features requeridas por el Champion Random Forest.

## 7. Request JSON

```json
{
  "lead_time": 120,
  "arrival_year": 2018,
  "arrival_month": 7,
  "arrival_date": 15,
  "no_of_special_requests": 0,
  "avg_price_per_room": 156.0,
  "market_segment_type": "Online",
  "no_of_weekend_nights": 1,
  "no_of_week_nights": 2,
  "type_of_meal_plan": "Meal Plan 1",
  "room_type_reserved": "Room_Type 1",
  "no_of_adults": 2,
  "no_of_children": 0,
  "required_car_parking_space": 0,
  "repeated_guest": 0,
  "no_of_previous_cancellations": 0,
  "no_of_previous_bookings_not_canceled": 0
}
```

## 8. Input Fields

| Campo | Tipo | Obligatorio | Descripcion |
| --- | --- | --- | --- |
| `lead_time` | integer | si | Dias entre reserva y llegada. |
| `arrival_year` | integer | si | Anio de llegada. |
| `arrival_month` | integer | si | Mes de llegada, entre 1 y 12. |
| `arrival_date` | integer | si | Dia de llegada, entre 1 y 31. |
| `no_of_special_requests` | integer | si | Numero de solicitudes especiales. |
| `avg_price_per_room` | float | si | Precio medio por habitacion. |
| `market_segment_type` | string | si | Canal o segmento de mercado. |
| `no_of_weekend_nights` | integer | si | Noches de fin de semana. |
| `no_of_week_nights` | integer | si | Noches entre semana. |
| `type_of_meal_plan` | string | si | Tipo de plan de comidas. |
| `room_type_reserved` | string | si | Tipo de habitacion reservada. |
| `no_of_adults` | integer | si | Numero de adultos. |
| `no_of_children` | integer | si | Numero de ninos. |
| `required_car_parking_space` | integer | si | Indica si requiere parking: `0` o `1`. |
| `repeated_guest` | integer | si | Indica si es huesped repetido: `0` o `1`. |
| `no_of_previous_cancellations` | integer | si | Cancelaciones previas del cliente. |
| `no_of_previous_bookings_not_canceled` | integer | si | Reservas previas no canceladas. |

## 9. Valores Iniciales Permitidos

Valores actuales usados por el frontend:

- `market_segment_type`: `Online`, `Offline`, `Corporate`, `Complementary`, `Aviation`.
- `room_type_reserved`: `Room_Type 1`, `Room_Type 2`, `Room_Type 3`, `Room_Type 4`, `Room_Type 5`.

Valores pendientes de cerrar con ML Core:

- Lista definitiva de `type_of_meal_plan`.
- Rango maximo recomendado para campos numericos.
- Tratamiento de categorias no vistas durante entrenamiento.

## 10. Response JSON

```json
{
  "prediction_id": "uuid-generado",
  "prediction": "Canceled",
  "prediction_label": 1,
  "probability": 0.72,
  "risk_level": "high",
  "risk_label": "Alto",
  "model_version": "random_forest_champion_v0.1.0",
  "main_factors": [
    "Solicitudes especiales",
    "Precio medio por habitacion",
    "Antelacion de la reserva"
  ],
  "risk_factors": [
    {
      "feature": "no_of_special_requests",
      "label": "Solicitudes especiales",
      "current_value": "0",
      "reference_value": "1",
      "impact_percentage_points": 54.7,
      "action": "Contactar al huesped para personalizar la estancia y reforzar su compromiso."
    }
  ],
  "recommendation": "Activar contacto proactivo, confirmar intencion de viaje y proteger inventario con lista de espera."
}
```

## 11. Output Fields

| Campo | Tipo | Descripcion |
| --- | --- | --- |
| `prediction_id` | string | UUID unico del registro de auditoria persistido antes de devolver la respuesta. |
| `prediction` | string | Clase predicha: `Canceled` o `Not_Canceled`. |
| `prediction_label` | integer | Codificacion numerica inicial: `1` cancelada, `0` no cancelada. |
| `probability` | float | Probabilidad estimada de cancelacion entre `0` y `1`. |
| `risk_level` | string | Nivel tecnico: `low`, `medium` o `high`. |
| `risk_label` | string | Etiqueta visible: `Bajo`, `Medio` o `Alto`. |
| `model_version` | string | Version del modelo usado. |
| `main_factors` | array[string] | Etiquetas de los factores locales ordenados por impacto estimado. |
| `risk_factors` | array[object] | Hasta tres variables que elevan el riesgo frente a referencias historicas de reservas no canceladas. Incluye valor actual, referencia, impacto en puntos porcentuales y accion sugerida. |
| `recommendation` | string | Recomendacion operativa para el equipo hotelero. |

`risk_factors` es una explicacion local por contrafactuales: recalcula la probabilidad al sustituir cada variable por un valor de referencia historico. Orienta la priorizacion operativa, pero no implica causalidad.

## 12. Feedback Endpoint

### `POST /feedback`

Guarda feedback de usuario y datos de prediccion para monitorizar performance y preparar futuros reentrenamientos.

#### Request JSON

```json
{
  "input_data": {
    "lead_time": 120,
    "arrival_year": 2018,
    "arrival_month": 7,
    "arrival_date": 15,
    "no_of_special_requests": 0,
    "avg_price_per_room": 156.0,
    "market_segment_type": "Online",
    "no_of_weekend_nights": 1,
    "no_of_week_nights": 2,
    "type_of_meal_plan": "Meal Plan 1",
    "room_type_reserved": "Room_Type 1",
    "no_of_adults": 2,
    "no_of_children": 0,
    "required_car_parking_space": 0,
    "repeated_guest": 0,
    "no_of_previous_cancellations": 0,
    "no_of_previous_bookings_not_canceled": 0
  },
  "prediction": "Canceled",
  "probability": 0.8338,
  "risk_level": "high",
  "model_version": "random_forest_champion_v0.1.0",
  "user_feedback": "unknown",
  "actual_status": null,
  "comments": "Feedback de validacion operativa.",
  "source": "web_app"
}
```

#### Response `200 OK`

```json
{
  "status": "stored",
  "record_id": "uuid-generado",
  "stored": true
}
```

Valores permitidos:

- `prediction`: `Canceled` o `Not_Canceled`.
- `risk_level`: `low`, `medium` o `high`.
- `user_feedback`: `correct`, `incorrect` o `unknown`.
- `actual_status`: `Canceled`, `Not_Canceled` o `null`.

Almacenamiento actual:

```text
SQLite local mediante SQLAlchemy.
PostgreSQL en Amazon RDS para el despliegue AWS.
```

La conexión se configura mediante `DATABASE_URL`. La API nunca devuelve credenciales ni endpoints privados.

## 13. Prediction Audit

Cada respuesta correcta de `POST /predict` queda persistida en `prediction_logs` antes de devolver `200 OK`. El registro incluye:

- `prediction_id` y timestamp UTC.
- Input validado completo.
- Prediccion, etiqueta numerica, probabilidad y nivel de riesgo.
- Version del modelo y fuente de la operacion.

Si la persistencia falla, la API no devuelve una prediccion correcta sin auditar. El campo adicional `prediction_id` es compatible con clientes anteriores que ignoren campos no utilizados.

## 14. Feedback Summary

### `GET /feedback/summary`

Devuelve un resumen minimo de registros de feedback persistidos.

#### Response `200 OK`

```json
{
  "total_records": 1,
  "storage": "postgresql"
}
```

`storage` puede ser `sqlite` en local o `postgresql` en AWS.

## 15. Data Drift Monitoring

### `GET /monitoring/drift`

Compara los inputs persistidos mediante feedback con el perfil versionado del conjunto de entrenamiento. No necesita conocer todavía el resultado real de la reserva.

#### Response `200 OK` con muestra insuficiente

```json
{
  "profile_version": "training_reference_v1",
  "generated_at": "2026-07-15T10:00:00+00:00",
  "reference_rows": 25391,
  "current_rows": 2,
  "minimum_current_rows": 100,
  "thresholds": {
    "moderate": 0.1,
    "high": 0.25
  },
  "status": "insufficient_data",
  "max_psi": null,
  "drifted_features": [],
  "features": [],
  "message": "At least 100 current records are required; only 2 are available."
}
```

Con al menos 100 registros validos, `features` incluye el nombre, tipo, PSI y estado de cada variable. Los estados globales posibles son:

- `insufficient_data`: no existe una muestra minima fiable.
- `stable`: todas las variables tienen PSI inferior a `0.10`.
- `warning`: existe drift moderado y no existe drift alto.
- `drift_detected`: al menos una variable tiene PSI igual o superior a `0.25`.

Este endpoint es informativo. Una alerta nunca promociona ni reemplaza automaticamente el modelo Champion.

## 16. Error Response

FastAPI devolvera errores de validacion con status `422` si faltan campos o los tipos no son validos.

Formato esperado:

```json
{
  "detail": [
    {
      "loc": ["body", "lead_time"],
      "msg": "Input should be a valid integer",
      "type": "int_type"
    }
  ]
}
```

## 17. Reglas Provisionales

- La forma de la respuesta no debe cambiar sin actualizar este contrato.
- El frontend no debe depender de campos no definidos aqui.
- El modelo real debe respetar este contrato o proponer una actualizacion documentada.
- `GET /model/info` debe reflejar la version y estado real del modelo cargado.
- `GET /reservations/demo` debe devolver `input_data` compatible con `POST /predict`.
- Cada respuesta `200 OK` de `POST /predict` debe tener un registro con el mismo `prediction_id`.
- `GET /monitoring/drift` debe usar el perfil versionado y declarar `insufficient_data` cuando no alcance la muestra minima.

## 18. Pendiente

- Confirmar inputs definitivos con ML Core.
- Mantener sincronizado el contrato si el pipeline de preprocesamiento cambia.
- Mantener sincronizada la version del Champion si se promociona un nuevo modelo.
- Confirmar estrategia de categorias no vistas.
- Confirmar si la probabilidad corresponde siempre a la clase `Canceled`.
- Mantener sincronizada la capa SQLAlchemy si cambia el esquema de feedback.
- Cambiar la fuente de Data Drift desde feedback a `prediction_logs` para observar todo el trafico de inferencia.
