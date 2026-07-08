# API Contract - Hotel Insights

Este contrato define la comunicacion inicial entre la aplicacion web y el backend de prediccion.

Estado: provisional hasta confirmar el Champion Model y el pipeline final de preprocesamiento.

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

## 4. Prediction Endpoint

### `POST /predict`

Calcula el riesgo de cancelacion de una reserva.

El endpoint debe aceptar un JSON con los campos iniciales del formulario actual. Estos campos coinciden con el mock frontend y con features candidatas del dataset.

## 5. Request JSON

```json
{
  "lead_time": 120,
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

## 6. Input Fields

| Campo | Tipo | Obligatorio | Descripcion |
| --- | --- | --- | --- |
| `lead_time` | integer | si | Dias entre reserva y llegada. |
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

## 7. Valores Iniciales Permitidos

Valores actuales usados por el frontend:

- `market_segment_type`: `Online`, `Offline`, `Corporate`, `Complementary`, `Aviation`.
- `room_type_reserved`: `Room_Type 1`, `Room_Type 2`, `Room_Type 3`, `Room_Type 4`, `Room_Type 5`.

Valores pendientes de cerrar con ML Core:

- Lista definitiva de `type_of_meal_plan`.
- Rango maximo recomendado para campos numericos.
- Tratamiento de categorias no vistas durante entrenamiento.

## 8. Response JSON

```json
{
  "prediction": "Canceled",
  "prediction_label": 1,
  "probability": 0.72,
  "risk_level": "high",
  "risk_label": "Alto",
  "model_version": "mock_api_v0",
  "main_factors": [
    "Lead time elevado",
    "Sin solicitudes especiales",
    "Segmento con cancelacion frecuente"
  ],
  "recommendation": "Activar contacto proactivo, confirmar intencion de viaje y proteger inventario con lista de espera."
}
```

## 9. Output Fields

| Campo | Tipo | Descripcion |
| --- | --- | --- |
| `prediction` | string | Clase predicha: `Canceled` o `Not_Canceled`. |
| `prediction_label` | integer | Codificacion numerica inicial: `1` cancelada, `0` no cancelada. |
| `probability` | float | Probabilidad estimada de cancelacion entre `0` y `1`. |
| `risk_level` | string | Nivel tecnico: `low`, `medium` o `high`. |
| `risk_label` | string | Etiqueta visible: `Bajo`, `Medio` o `Alto`. |
| `model_version` | string | Version del modelo o mock usado. |
| `main_factors` | array[string] | Factores explicativos principales. |
| `recommendation` | string | Recomendacion operativa para el equipo hotelero. |

## 10. Error Response

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

## 11. Reglas Provisionales

- El backend inicial puede devolver prediccion mock mientras no exista Champion Model.
- La forma de la respuesta no debe cambiar sin actualizar este contrato.
- El frontend no debe depender de campos no definidos aqui.
- El modelo real debe respetar este contrato o proponer una actualizacion documentada.

## 12. Pendiente

- Confirmar inputs definitivos con ML Core.
- Confirmar pipeline de preprocesamiento.
- Confirmar Champion Model.
- Confirmar versionado real de modelo.
- Confirmar estrategia de categorias no vistas.
- Confirmar si la probabilidad corresponde siempre a la clase `Canceled`.
