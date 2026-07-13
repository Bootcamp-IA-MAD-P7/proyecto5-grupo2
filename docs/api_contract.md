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

## 2. Base URL local

```text
http://localhost:8000
```

El frontend puede configurar esta URL mediante:

```text
VITE_API_URL
```

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

## 5. Prediction Endpoint

### `POST /predict`

Calcula el riesgo de cancelacion de una reserva.

El endpoint acepta un JSON con los campos del formulario y las features requeridas por el Champion Random Forest.

## 6. Request JSON

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

## 7. Input Fields

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

## 8. Valores Iniciales Permitidos

Valores actuales usados por el frontend:

- `market_segment_type`: `Online`, `Offline`, `Corporate`, `Complementary`, `Aviation`.
- `room_type_reserved`: `Room_Type 1`, `Room_Type 2`, `Room_Type 3`, `Room_Type 4`, `Room_Type 5`.

Valores pendientes de cerrar con ML Core:

- Lista definitiva de `type_of_meal_plan`.
- Rango maximo recomendado para campos numericos.
- Tratamiento de categorias no vistas durante entrenamiento.

## 9. Response JSON

```json
{
  "prediction": "Canceled",
  "prediction_label": 1,
  "probability": 0.72,
  "risk_level": "high",
  "risk_label": "Alto",
  "model_version": "random_forest_champion_v0.1.0",
  "main_factors": [
    "Lead time elevado",
    "Sin solicitudes especiales",
    "Segmento con cancelacion frecuente"
  ],
  "recommendation": "Activar contacto proactivo, confirmar intencion de viaje y proteger inventario con lista de espera."
}
```

## 10. Output Fields

| Campo | Tipo | Descripcion |
| --- | --- | --- |
| `prediction` | string | Clase predicha: `Canceled` o `Not_Canceled`. |
| `prediction_label` | integer | Codificacion numerica inicial: `1` cancelada, `0` no cancelada. |
| `probability` | float | Probabilidad estimada de cancelacion entre `0` y `1`. |
| `risk_level` | string | Nivel tecnico: `low`, `medium` o `high`. |
| `risk_label` | string | Etiqueta visible: `Bajo`, `Medio` o `Alto`. |
| `model_version` | string | Version del modelo usado. |
| `main_factors` | array[string] | Factores explicativos principales. |
| `recommendation` | string | Recomendacion operativa para el equipo hotelero. |

## 11. Error Response

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

## 12. Reglas Provisionales

- La forma de la respuesta no debe cambiar sin actualizar este contrato.
- El frontend no debe depender de campos no definidos aqui.
- El modelo real debe respetar este contrato o proponer una actualizacion documentada.
- `GET /model/info` debe reflejar la version y estado real del modelo cargado.

## 13. Pendiente

- Confirmar inputs definitivos con ML Core.
- Mantener sincronizado el contrato si el pipeline de preprocesamiento cambia.
- Mantener sincronizada la version del Champion si se promociona un nuevo modelo.
- Confirmar estrategia de categorias no vistas.
- Confirmar si la probabilidad corresponde siempre a la clase `Canceled`.
