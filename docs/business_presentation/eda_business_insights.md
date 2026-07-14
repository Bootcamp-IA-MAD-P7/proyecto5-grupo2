# EDA Business Insights

## Objetivo

Este documento traduce los principales hallazgos del analisis exploratorio a lenguaje de negocio para apoyar la presentacion cliente de Hotel Insights.

No sustituye al notebook tecnico. Su funcion es explicar que significan los graficos y como se conectan con decisiones operativas en reservas, revenue management y operaciones.

## Lecturas clave

### 1. Las cancelaciones son un problema relevante, no marginal

El dataset muestra dos clases:

| Clase | Peso aproximado |
| --- | ---: |
| `Not_Canceled` | 67.2% |
| `Canceled` | 32.8% |

Lectura de negocio:

- Casi una de cada tres reservas acaba cancelada.
- El problema tiene impacto suficiente para justificar una herramienta de priorizacion.
- No basta con mirar ocupacion prevista; hace falta distinguir reservas firmes de reservas con riesgo.

Uso en presentacion:

> Hotel Insights ayuda a convertir una cartera de reservas incierta en una lista accionable de llegadas que conviene revisar.

### 2. La antelacion de reserva es una senal fuerte

`lead_time` aparece como una de las variables con mayor peso en el modelo Champion.

Lectura de negocio:

- Las reservas hechas con mucha antelacion suelen tener mas tiempo para cambiar de plan.
- El equipo puede vigilar con mas cuidado reservas lejanas que combinan otras senales de riesgo.
- La antelacion no debe interpretarse sola, sino junto al canal, precio, historial y comportamiento de la reserva.

Uso en presentacion:

> Cuanto mas lejos queda la llegada, mas importante es saber si merece seguimiento preventivo.

### 3. Las solicitudes especiales aportan compromiso

`no_of_special_requests` tiene una senal relevante en el modelo.

Lectura de negocio:

- Una reserva con solicitudes especiales suele indicar mas implicacion del huesped.
- Una reserva sin solicitudes especiales puede requerir mas contexto antes de considerarse segura.
- Esta variable ayuda a separar reservas parecidas en precio o canal, pero con distinto nivel de compromiso.

Uso en presentacion:

> No todas las reservas con el mismo precio o fecha tienen el mismo grado de compromiso.

### 4. Canal y segmento ayudan a priorizar

`market_segment_type` aparece entre las variables que ayudan a diferenciar patrones de cancelacion.

Lectura de negocio:

- El canal de entrada puede reflejar comportamientos distintos de reserva.
- Algunos segmentos pueden concentrar mas incertidumbre que otros.
- Esta lectura ayuda a orientar acciones: confirmar, contactar, revisar condiciones o ajustar seguimiento comercial.

Uso en presentacion:

> La herramienta no mira solo la reserva aislada; tambien interpreta el contexto comercial en el que se genero.

### 5. Precio y calendario completan la lectura de riesgo

Variables como `avg_price_per_room`, `arrival_month`, `arrival_date` y noches reservadas ayudan al modelo a entender contexto.

Lectura de negocio:

- El precio medio puede indicar sensibilidad economica o patrones de demanda.
- El mes de llegada puede capturar estacionalidad.
- La duracion de estancia ayuda a valorar el impacto operativo y economico de una cancelacion.

Uso en presentacion:

> El riesgo se interpreta junto al valor de la estancia, no como una etiqueta aislada.

### 6. El modelo sirve para priorizar acciones, no para automatizar decisiones ciegas

El informe tecnico identifica falsos positivos y falsos negativos.

Lectura de negocio:

- Un falso positivo implica revisar una reserva que finalmente no se cancela.
- Un falso negativo implica no detectar una cancelacion real.
- Para negocio, perder una cancelacion no anticipada puede ser mas sensible que revisar una reserva de mas.
- Por eso la herramienta debe usarse como apoyo a equipos humanos, no como sustituto automatico de criterio operativo.

Uso en presentacion:

> Hotel Insights no reemplaza al equipo: ordena la revision para que el equipo actue antes y mejor.

## Mensaje ejecutivo

El EDA confirma que el problema de cancelaciones tiene volumen, patrones y variables accionables. Las senales mas utiles no son solo tecnicas: antelacion, canal, solicitudes especiales, precio y calendario tienen una interpretacion directa para equipos hoteleros.

La oportunidad de producto es clara: convertir predicciones en una cola de trabajo donde el equipo vea que reservas revisar primero, por que merece revisarlas y que aprendizaje queda registrado para futuras mejoras.

## Como usar estos insights en la presentacion

- Usar el desbalance del target para justificar el problema.
- Usar `lead_time` para explicar anticipacion y seguimiento preventivo.
- Usar `no_of_special_requests` para hablar de compromiso del huesped.
- Usar `market_segment_type` para conectar el modelo con canales comerciales.
- Usar el analisis de errores para explicar limitaciones y responsabilidad humana.
- Evitar prometer decisiones automaticas: presentar la app como herramienta de priorizacion.
