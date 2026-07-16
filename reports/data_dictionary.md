# Diccionario de datos

Dataset: Hotel Reservations Classification Dataset  
Archivo: `data/raw/hotel-reservations-classification-dataset/Hotel Reservations.csv`  
Filas confirmadas: 36.275  
Columnas confirmadas: 19  
Target: `booking_status`  
Tipo de problema: clasificacion supervisada binaria

## Objetivo del diccionario

Este documento describe las columnas del dataset y recoge las decisiones consolidadas tras la inspeccion, el EDA y el entrenamiento. Su funcion es dejar claro que representa cada variable, si se utiliza como feature, si es el target o si debe excluirse.

## Resumen del target

| Clase | Filas | Porcentaje aproximado |
|---|---:|---:|
| `Not_Canceled` | 24.390 | 67.2% |
| `Canceled` | 11.885 | 32.8% |

Interpretacion consolidada:

- El problema es binario: reserva cancelada o no cancelada.
- Existe desbalance moderado hacia `Not_Canceled`.
- La evaluacion del modelo no debe depender solo de `accuracy`.
- Se deberan revisar tambien `precision`, `recall`, `F1-score`, matriz de confusion y ROC-AUC si aplica.

## Diccionario de columnas

| Columna | Rol actual | Tipo esperado | Descripcion | Decision actual |
|---|---|---|---|---|
| `Booking_ID` | Excluir | Identificador | Codigo unico de la reserva. | Excluida del pipeline porque no generaliza a nuevas reservas. |
| `no_of_adults` | Feature | Numerica discreta | Numero de adultos incluidos en la reserva. | Utilizada por el pipeline. |
| `no_of_children` | Feature | Numerica discreta | Numero de ninos incluidos en la reserva. | Utilizada por el pipeline. |
| `no_of_weekend_nights` | Feature | Numerica discreta | Numero de noches de fin de semana reservadas. | Utilizada por el pipeline. |
| `no_of_week_nights` | Feature | Numerica discreta | Numero de noches entre semana reservadas. | Utilizada por el pipeline. |
| `type_of_meal_plan` | Feature | Categorica nominal | Tipo de plan de comidas seleccionado. | Utilizada con One-Hot Encoding. |
| `required_car_parking_space` | Feature | Binaria | Indica si la reserva requiere plaza de parking. | Utilizada por el pipeline. |
| `room_type_reserved` | Feature | Categorica nominal | Tipo de habitacion reservada. | Utilizada con One-Hot Encoding. |
| `lead_time` | Feature | Numerica discreta | Dias entre la reserva y la fecha de llegada. | Utilizada; es una de las variables con mayor senal predictiva. |
| `arrival_year` | Feature | Numerica temporal | Ano de llegada. | Utilizada por el pipeline actual. |
| `arrival_month` | Feature | Numerica temporal | Mes de llegada. | Utilizada para capturar estacionalidad. |
| `arrival_date` | Feature | Numerica temporal | Dia del mes de llegada. | Utilizada por el pipeline actual. |
| `market_segment_type` | Feature | Categorica nominal | Canal o segmento de mercado de la reserva. | Utilizada con One-Hot Encoding. |
| `repeated_guest` | Feature | Binaria | Indica si el cliente es repetido. | Utilizada por el pipeline. |
| `no_of_previous_cancellations` | Feature | Numerica discreta | Numero de cancelaciones anteriores del cliente. | Utilizada por el pipeline. |
| `no_of_previous_bookings_not_canceled` | Feature | Numerica discreta | Reservas anteriores no canceladas del cliente. | Utilizada por el pipeline. |
| `avg_price_per_room` | Feature | Numerica continua | Precio medio por habitacion. | Utilizada; su distribucion y rango se documentaron en el EDA. |
| `no_of_special_requests` | Feature | Numerica discreta | Numero de solicitudes especiales realizadas. | Utilizada; muestra relacion inversa con la cancelacion. |
| `booking_status` | Target | Categorica binaria | Estado final historico de la reserva. | Predecir esta columna. |

## Inspeccion tecnica confirmada

La inspeccion del CSV confirma que no hay valores nulos en ninguna columna. El pipeline actual no necesita imputacion para este dataset.

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

Interpretacion consolidada:

- El dataset esta completo a nivel de nulos, lo cual facilita la primera version del pipeline.
- `Booking_ID` tiene un valor unico por fila, por eso se confirma su exclusion.
- `lead_time` llega hasta 443 dias; conviene revisar su distribucion y posibles outliers en el EDA.
- `avg_price_per_room` llega hasta 540 y tambien requiere revision visual.
- Las variables binarias estan codificadas como 0/1 y podran tratarse como numericas o binarias segun el preprocessing.
- Las variables categoricas tienen pocas categorias y se procesan mediante One-Hot Encoding.

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

## Variables excluidas

- `Booking_ID`

Motivo: es un identificador unico. Puede ayudar a memorizar filas, pero no aporta una regla general para predecir nuevas reservas.

## Conclusiones confirmadas tras el EDA

- No existen valores nulos ni duplicados exactos en las 36.275 filas.
- `lead_time` presenta un rango de 0 a 443 dias y una mediana de 57; las reservas canceladas muestran mayor anticipacion que las no canceladas.
- `avg_price_per_room` presenta un rango de 0 a 540 y una mediana de 99,45; su relacion con la cancelacion existe, aunque es menos marcada que la de `lead_time`.
- `no_of_special_requests` muestra una relacion inversa con la cancelacion.
- `market_segment_type` y `repeated_guest` presentan diferencias relevantes en la tasa de cancelacion.
- Las variables temporales se mantienen en el contrato actual como columnas separadas y se evaluan dentro del pipeline reproducible.
- El desbalance es moderado: 67,24% `Not_Canceled` y 32,76% `Canceled`. Se usa F1 de `Canceled` como metrica principal y pesos balanceados cuando corresponde; no se aplica sobremuestreo sintetico.
- Las categorias se codifican con `OneHotEncoder(handle_unknown="ignore")`, por lo que valores no vistos no rompen la inferencia.
