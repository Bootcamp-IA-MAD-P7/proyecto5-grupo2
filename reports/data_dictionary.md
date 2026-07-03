# Diccionario inicial de datos

Dataset: Hotel Reservations Classification Dataset  
Archivo: `data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv`  
Filas confirmadas: 36.275  
Columnas confirmadas: 19  
Target: `booking_status`  
Tipo de problema: clasificacion supervisada binaria

## Objetivo del diccionario

Este documento describe las columnas del dataset antes del EDA profundo. Su funcion es dejar claro que representa cada variable, si sera candidata a feature, si sera target o si debe excluirse inicialmente.

El diccionario puede cambiar despues del EDA si aparecen problemas de calidad, leakage, valores raros o variables poco utiles.

## Resumen del target

| Clase | Filas | Porcentaje aproximado |
|---|---:|---:|
| `Not_Canceled` | 24.390 | 67.2% |
| `Canceled` | 11.885 | 32.8% |

Interpretacion inicial:

- El problema es binario: reserva cancelada o no cancelada.
- Existe desbalance moderado hacia `Not_Canceled`.
- La evaluacion del modelo no debe depender solo de `accuracy`.
- Se deberan revisar tambien `precision`, `recall`, `F1-score`, matriz de confusion y ROC-AUC si aplica.

## Diccionario de columnas

| Columna | Rol inicial | Tipo esperado | Descripcion | Decision inicial |
|---|---|---|---|---|
| `Booking_ID` | Excluir | Identificador | Codigo unico de la reserva. | No usar como feature porque no generaliza a nuevas reservas. |
| `no_of_adults` | Feature | Numerica discreta | Numero de adultos incluidos en la reserva. | Usar inicialmente. |
| `no_of_children` | Feature | Numerica discreta | Numero de ninos incluidos en la reserva. | Usar inicialmente. |
| `no_of_weekend_nights` | Feature | Numerica discreta | Numero de noches de fin de semana reservadas. | Usar inicialmente. |
| `no_of_week_nights` | Feature | Numerica discreta | Numero de noches entre semana reservadas. | Usar inicialmente. |
| `type_of_meal_plan` | Feature | Categorica nominal | Tipo de plan de comidas seleccionado. | Usar inicialmente con encoding. |
| `required_car_parking_space` | Feature | Binaria | Indica si la reserva requiere plaza de parking. | Usar inicialmente. |
| `room_type_reserved` | Feature | Categorica nominal | Tipo de habitacion reservada. | Usar inicialmente con encoding. |
| `lead_time` | Feature | Numerica discreta | Dias entre la reserva y la fecha de llegada. | Usar inicialmente; revisar distribucion y outliers. |
| `arrival_year` | Feature | Numerica temporal | Ano de llegada. | Usar inicialmente; revisar si aporta o introduce sesgo temporal. |
| `arrival_month` | Feature | Numerica temporal | Mes de llegada. | Usar inicialmente; puede capturar estacionalidad. |
| `arrival_date` | Feature | Numerica temporal | Dia del mes de llegada. | Usar inicialmente; revisar utilidad real. |
| `market_segment_type` | Feature | Categorica nominal | Canal o segmento de mercado de la reserva. | Usar inicialmente con encoding. |
| `repeated_guest` | Feature | Binaria | Indica si el cliente es repetido. | Usar inicialmente. |
| `no_of_previous_cancellations` | Feature | Numerica discreta | Numero de cancelaciones anteriores del cliente. | Usar inicialmente; posible variable predictiva fuerte. |
| `no_of_previous_bookings_not_canceled` | Feature | Numerica discreta | Reservas anteriores no canceladas del cliente. | Usar inicialmente. |
| `avg_price_per_room` | Feature | Numerica continua | Precio medio por habitacion. | Usar inicialmente; revisar outliers. |
| `no_of_special_requests` | Feature | Numerica discreta | Numero de solicitudes especiales realizadas. | Usar inicialmente. |
| `booking_status` | Target | Categorica binaria | Estado final historico de la reserva. | Predecir esta columna. |

## Inspeccion tecnica inicial

La inspeccion ligera del CSV confirma que no hay valores nulos en ninguna columna. Esto simplifica el primer baseline, porque no necesitamos imputacion inmediata antes de entrenar un modelo inicial.

| Columna | Nulos | Unicos | Rango o ejemplos |
|---|---:|---:|---|
| `Booking_ID` | 0 | 36.275 | Ejemplos: `INN00001`, `INN00002`, `INN00003` |
| `no_of_adults` | 0 | 5 | Min: 0, Max: 4 |
| `no_of_children` | 0 | 6 | Min: 0, Max: 10 |
| `no_of_weekend_nights` | 0 | 8 | Min: 0, Max: 7 |
| `no_of_week_nights` | 0 | 18 | Min: 0, Max: 17 |
| `type_of_meal_plan` | 0 | 4 | Ejemplos: `Meal Plan 1`, `Not Selected`, `Meal Plan 2` |
| `required_car_parking_space` | 0 | 2 | Min: 0, Max: 1 |
| `room_type_reserved` | 0 | 7 | Ejemplos: `Room_Type 1`, `Room_Type 4`, `Room_Type 2` |
| `lead_time` | 0 | 352 | Min: 0, Max: 443 |
| `arrival_year` | 0 | 2 | Min: 2017, Max: 2018 |
| `arrival_month` | 0 | 12 | Min: 1, Max: 12 |
| `arrival_date` | 0 | 31 | Min: 1, Max: 31 |
| `market_segment_type` | 0 | 5 | Ejemplos: `Offline`, `Online`, `Corporate` |
| `repeated_guest` | 0 | 2 | Min: 0, Max: 1 |
| `no_of_previous_cancellations` | 0 | 9 | Min: 0, Max: 13 |
| `no_of_previous_bookings_not_canceled` | 0 | 59 | Min: 0, Max: 58 |
| `avg_price_per_room` | 0 | 3.930 | Min: 0, Max: 540 |
| `no_of_special_requests` | 0 | 6 | Min: 0, Max: 5 |
| `booking_status` | 0 | 2 | `Not_Canceled`, `Canceled` |

Interpretacion inicial:

- El dataset esta completo a nivel de nulos, lo cual facilita la primera version del pipeline.
- `Booking_ID` tiene un valor unico por fila, por eso se confirma su exclusion inicial.
- `lead_time` llega hasta 443 dias; conviene revisar su distribucion y posibles outliers en el EDA.
- `avg_price_per_room` llega hasta 540 y tambien requiere revision visual.
- Las variables binarias estan codificadas como 0/1 y podran tratarse como numericas o binarias segun el preprocessing.
- Las variables categoricas tienen pocas categorias, por lo que One-Hot Encoding parece una opcion inicial razonable.

## Variables numericas candidatas

- `no_of_adults`
- `no_of_children`
- `no_of_weekend_nights`
- `no_of_week_nights`
- `lead_time`
- `arrival_year`
- `arrival_month`
- `arrival_date`
- `no_of_previous_cancellations`
- `no_of_previous_bookings_not_canceled`
- `avg_price_per_room`
- `no_of_special_requests`

## Variables categoricas candidatas

- `type_of_meal_plan`
- `room_type_reserved`
- `market_segment_type`

## Variables binarias candidatas

- `required_car_parking_space`
- `repeated_guest`

## Variables excluidas inicialmente

- `Booking_ID`

Motivo: es un identificador unico. Puede ayudar a memorizar filas, pero no aporta una regla general para predecir nuevas reservas.

## Pendientes de confirmar en EDA

- Duplicados.
- Valores raros o categorias poco frecuentes.
- Distribucion de `lead_time` y `avg_price_per_room`.
- Relacion de cada feature con `booking_status`.
- Posibles variables temporales que convenga transformar.
- Si el desbalance requiere tratamiento especifico.
