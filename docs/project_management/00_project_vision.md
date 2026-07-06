# Project Vision - Hotel Insights

## 1. Objetivo del proyecto

Hotel Insights es una solución de clasificación aplicada al sector hotelero cuyo objetivo es predecir si una reserva será cancelada o no antes de la fecha de llegada.

El proyecto busca combinar Machine Learning, aplicación web, documentación técnica, presentación de negocio y buenas prácticas de trabajo colaborativo en GitHub.

## 2. Problema de negocio

Las cancelaciones de reservas afectan a la ocupación, la previsión de ingresos y la planificación operativa de hoteles y plataformas de reservas.

El sistema permitirá estimar el riesgo de cancelación de una reserva a partir de variables disponibles antes de la llegada, ayudando a priorizar acciones comerciales u operativas.

## 3. Producto esperado

El producto final debe incluir:

- Un modelo de clasificación funcional.
- Un análisis exploratorio de datos con visualizaciones.
- Métricas de rendimiento y control de overfitting.
- Una aplicación web para introducir datos de una reserva y obtener una predicción.
- Un sistema básico de feedback o registro de predicciones si se alcanza el nivel medio.
- Documentación técnica y de negocio.
- Una presentación para cliente y una presentación técnica.
- Un repositorio ordenado con ramas, commits limpios y evidencias de verificación.

## 4. Enfoque como proyecto real de software

Aunque nace como proyecto académico, se trabajará como si fuese un producto web real:

- Separación entre frontend, backend, ML y documentación.
- Contrato claro entre modelo y aplicación.
- Versionado de modelos.
- Entregas por ramas y Pull Requests.
- Tests mínimos.
- Automatización con GitHub Actions cuando sea viable.
- Docker como objetivo avanzado.
- Roadmap por niveles: esencial, medio, avanzado y experto.

## 5. Metodología SDD / SPEC

El proyecto seguirá una metodología basada en SPEC / SDD.

La carpeta `.specify/` será la fuente de verdad para:

- Intención del proyecto.
- Especificación técnica.
- Plan por fases.
- Tareas verificables.

Antes de implementar cambios relevantes, se debe comprobar que no contradicen la SPEC.

## 6. Trabajo con agentes de IA

Los agentes de IA podrán ayudar al equipo, pero deben trabajar con reglas claras:

- Leer primero `.specify/`.
- Trabajar sobre una rama concreta.
- No modificar áreas fuera de su rol sin avisar.
- Explicar archivos afectados antes de implementar.
- Dejar comandos de verificación.
- Documentar decisiones relevantes.

Se proponen agentes por rol:

- ML Core.
- App / Producto.
- MLOps / Experto.
- QA / Docs / Presentación.

## 7. UX/UI e identidad visual

La app debe transmitir una experiencia profesional y coherente con el sector hotelero.

Más adelante se definirá una guía visual con:

- Paleta de colores.
- Tipografías.
- Tono de comunicación.
- Componentes principales.
- Reglas de layout.
- Capturas para presentación.

Esta fase no rediseña todavía la app, solo reconoce que UX/UI forma parte del producto final.

## 8. Entregables principales

- Repositorio GitHub ordenado.
- README profesional.
- Dataset y EDA documentados.
- Modelo Champion seleccionado.
- App web funcional.
- Informe técnico.
- Presentación de negocio.
- Presentación técnica.
- Evidencias de validación.
- Checklist final de entrega.

## 9. Principio de trabajo

Primero se protegerá el Nivel Esencial.

Después se añadirán mejoras de Nivel Medio, Avanzado y Experto solo si no ponen en riesgo la entrega principal.