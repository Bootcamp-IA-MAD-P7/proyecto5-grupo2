# Frontend Beta - Flujo operativo

## Objetivo

Crear una interfaz alternativa para Hotel Insights centrada en el uso real del producto: revisar reservas, calcular riesgo de cancelacion, decidir la siguiente accion y registrar feedback.

Esta beta no sustituye al frontend actual. Se activa con:

```text
/?variant=beta
```

## Persona principal

Responsable de reservas, revenue management u operaciones de un hotel o plataforma de reservas.

Necesita:

- Detectar reservas con riesgo de cancelacion antes de la llegada.
- Priorizar que reservas revisar primero.
- Ver una recomendacion operativa clara.
- Registrar si la prediccion fue util para mejorar el modelo.

No necesita:

- Login simulado.
- Navegacion compleja.
- Pantallas decorativas sin accion clara.
- Cambios de seccion que no respondan a un flujo de trabajo real.

## Flujo de usuario

1. Ver cola de reservas pendientes de revision.
2. Seleccionar una reserva.
3. Revisar o ajustar los datos principales.
4. Calcular riesgo con el Champion Model.
5. Leer probabilidad, nivel de riesgo, factores y recomendacion.
6. Registrar feedback:
   - Prediccion correcta.
   - Prediccion a revisar.
   - Aun no se sabe.
7. El feedback queda disponible para monitorizacion y futuros reentrenamientos.

## Pantalla propuesta

La beta usa una sola pantalla operativa:

- Cabecera con version del modelo y numero de feedbacks.
- Resumen de reservas en revision.
- Cola de llegadas.
- Panel de datos de reserva.
- Panel de decision operativa.
- Acciones de feedback.

## Contrato backend usado

- `GET /model/info`.
- `POST /predict`.
- `POST /feedback`.
- `GET /feedback/summary`.

## Criterio de exito

La app debe poder explicar su utilidad en menos de 30 segundos:

> "Selecciono una reserva, calculo su riesgo, veo que accion tomar y registro feedback para mejorar el modelo."
