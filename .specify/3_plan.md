# SPEC 3 - Plan

Este plan organiza el trabajo por fases verificables y frentes permanentes. Cada fase debe dejar el proyecto en un estado ejecutable, revisable o demostrable.

## Frentes permanentes

- ML Core: dataset, EDA, preprocessing, baseline, ensemble y Champion Model.
- App / Producto: app, formulario, inferencia, feedback, almacenamiento y demo.
- MLOps / Experto: Docker, tests, red neuronal, A/B Testing, drift y auto-reemplazo.
- QA / Documentacion / Presentacion: SPEC, Jira, README, checklist, informe, capturas, validacion manual y presentaciones.

## Regla de prioridad

El Nivel Esencial se cierra antes de depender de componentes expertos. La capa experta se construye encima de un sistema esencial ya funcional.

## Fase 0 - Alineacion y preparacion

### Objetivo

Dejar listo el contrato de trabajo, tablero y acuerdos minimos antes de programar.

### Responsables

- ML Core: define criterios de dataset y target candidato.
- App / Producto: define tecnologia candidata de app y mock inicial.
- MLOps / Experto: define arquitectura Champion/Challenger.
- QA / Docs: mantiene Jira, checklist y `.specify/`.

### Tareas paralelas

- ML Core: revisar datasets candidatos y documentar pros/contras.
- App / Producto: dibujar flujo de app sin implementar.
- MLOps / Experto: proponer ciclo de modelos y versiones.
- QA / Docs: pasar tickets iniciales a Jira y preparar README base.

### Entregables

- `.specify/` creado.
- Jira como herramienta oficial de gestion.
- README con descripcion inicial.
- Decision pendiente o tomada sobre dataset.

### Verificacion

- Existen los 4 archivos SPEC.
- Hay tablero con columnas y tickets iniciales.
- El equipo entiende que no se programa sin dataset y target claros.

### Riesgos

- Dataset indefinido retrasa ML Core.
- App se disena sin conocer inputs reales.
- El equipo empieza codigo antes de cerrar criterios minimos.

## Fase 1 - Dataset, EDA y contrato de datos

### Objetivo

Elegir dataset, definir target, hacer EDA inicial y cerrar el contrato de datos.

### Responsables

- ML Core lidera dataset, target y EDA.
- App / Producto traduce features a inputs de usuario.
- MLOps / Experto revisa riesgos de leakage y versionado.
- QA / Docs documenta decisiones, graficos y tabla de variables.

### Tareas paralelas

- ML Core: cargar dataset, revisar nulos, duplicados, tipos y target.
- App / Producto: listar inputs posibles y validar si son comprensibles para usuario.
- MLOps / Experto: definir separacion train/valid/test y estrategia de versionado.
- QA / Docs: capturar graficos, crear diccionario de datos y actualizar README.

### Entregables

- Dataset en `data/raw/` o instrucciones claras de descarga.
- Diccionario de datos.
- EDA inicial.
- Target documentado.
- Primera lista de features.

### Verificacion

- El equipo puede explicar que se predice y con que columnas.
- Existen visualizaciones relevantes para clasificacion.
- No hay leakage evidente sin documentar.

### Riesgos

- Target desbalanceado.
- Dataset pequeno o pobre.
- Variables dificiles de convertir en formulario.

## Fase 2 - Nivel Esencial MVP

### Objetivo

Construir una primera solucion completa: preprocessing, baseline, metricas y app funcional.

### Responsables

- ML Core lidera baseline y metricas.
- App / Producto integra prediccion inicial.
- MLOps / Experto prepara estructura de artefactos y smoke checks.
- QA / Docs valida app, actualiza informe y README.

### Tareas paralelas

- ML Core: crear pipeline de preprocesamiento y baseline.
- App / Producto: crear app minima con formulario y prediccion.
- MLOps / Experto: definir guardado de modelo y version.
- QA / Docs: registrar experimento, revisar metricas y documentar uso.

### Entregables

- Baseline entrenado.
- Metricas obligatorias iniciales.
- Matriz de confusion.
- App ejecutable.
- Informe tecnico inicial.

### Verificacion

- La app recibe datos y devuelve prediccion.
- El baseline tiene train y validacion.
- La metrica principal es F1-score de la clase `Canceled`.
- La diferencia train-validacion de F1-score de `Canceled` es menor a 0.05 o queda marcada como bloqueo.

### Riesgos

- Overfitting superior al 5%.
- App rompe por diferencias entre inputs y features.
- Metricas mal elegidas para clases desbalanceadas.

## Fase 3 - Nivel Medio robusto

### Objetivo

Mejorar el modelo con ensemble, validacion cruzada, tuning, Champion Model y feedback.

### Responsables

- ML Core lidera ensemble, cross-validation y tuning.
- App / Producto implementa feedback y almacenamiento inicial.
- MLOps / Experto define Challenger y preparacion para A/B.
- QA / Docs mantiene tabla de experimentos e interpretacion.

### Tareas paralelas

- ML Core: entrenar Random Forest o Gradient Boosting y comparar con baseline.
- App / Producto: guardar feedback mediante la capa SQLAlchemy y validar SQLite/PostgreSQL según entorno.
- MLOps / Experto: crear reglas de versionado Champion/Challenger.
- QA / Docs: actualizar informe con feature importance y analisis de errores.

### Entregables

- Modelo ensemble.
- Validacion cruzada.
- Tuning de hiperparametros.
- Champion seleccionado.
- Feedback guardado.
- Tabla de experimentos completa.

### Verificacion

- Champion supera baseline en F1-score de la clase `Canceled` o se justifica por estabilidad.
- Champion cumple overfitting inferior al 5%.
- Feedback queda persistido y revisable.

### Riesgos

- Tuning mejora train pero empeora validacion.
- Feedback no tiene schema claro.
- Feature importance se interpreta de forma exagerada.

## Fase 4 - Nivel Avanzado operativo

### Objetivo

Preparar el proyecto para ejecucion controlada con tests, Docker, almacenamiento persistente y despliegue web.

### Responsables

- ML Core define umbrales minimos de metricas.
- App / Producto conecta almacenamiento persistente.
- MLOps / Experto lidera Docker y tests tecnicos.
- QA / Docs ejecuta smoke test, capturas y guia de instalacion.

### Tareas paralelas

- ML Core: fijar metricas minimas y revisar overfitting final.
- App / Producto: validar guardado de predicciones y feedback.
- MLOps / Experto: crear Dockerfile, docker-compose si aplica y tests.
- QA / Docs: documentar comandos, capturas y checklist de demo.

### Entregables

- Tests minimos.
- Docker funcional o preparado.
- Base de datos o almacenamiento persistente.
- README con instalacion y ejecucion.
- Smoke test documentado.
- Despliegue HTTPS reproducible y automatizado.

### Verificacion

- Tests pasan.
- La app arranca con el comando documentado.
- Docker levanta la app o queda documentado el bloqueo.
- El despliegue carga el Champion, conecta PostgreSQL y supera el health check.

### Estado alcanzado

- SQLite disponible para desarrollo local y PostgreSQL en Amazon RDS para el entorno desplegado.
- Docker Compose ejecutado en Amazon EC2.
- Amazon CloudFront proporciona acceso HTTPS público.
- GitHub Actions despliega desde `develop` mediante OIDC y AWS Systems Manager.
- Operación documentada en `docs/aws_deployment.md`.

### Riesgos

- Dependencias no reproducibles.
- Docker consume demasiado tiempo.
- Tests se escriben tarde y detectan problemas estructurales.

## Fase 5 - Nivel Experto incremental

### Objetivo

Sumar red neuronal, A/B Testing, Data Drift y auto-reemplazo sin romper el Champion estable.

### Responsables

- ML Core compara resultados contra Champion.
- App / Producto muestra version de modelo y resultados de feedback.
- MLOps / Experto lidera red neuronal, A/B, drift y auto-reemplazo.
- QA / Docs documenta arquitectura MLOps y limitaciones.

### Tareas paralelas

- ML Core: preparar comparacion final de modelos.
- App / Producto: adaptar app para registrar `model_version`.
- MLOps / Experto: implementar o simular A/B, drift y auto-reemplazo.
- QA / Docs: preparar explicacion visual del ciclo MLOps.

### Entregables

- Red neuronal entrenada y comparada.
- A/B Testing real o simulado.
- Data Drift calculado.
- Auto-reemplazo condicionado por reglas.
- Reporte o dashboard de monitoreo.

### Verificacion

- Ningun componente experto rompe la app esencial.
- El reemplazo solo ocurre si se cumplen reglas documentadas.
- Las limitaciones quedan explicadas para defensa tecnica.

### Riesgos

- Red neuronal no mejora.
- Drift se vuelve demasiado complejo.
- Auto-reemplazo parece automatico sin control de calidad.

## Fase 6 - Cierre y defensa

### Objetivo

Congelar version final, verificar entregables y preparar presentaciones.

### Responsables

- ML Core valida metricas finales.
- App / Producto prepara demo.
- MLOps / Experto ejecuta smoke test experto.
- QA / Docs lidera presentaciones y checklist.

### Tareas paralelas

- ML Core: revisar tabla de experimentos y Champion final.
- App / Producto: probar flujo completo de usuario.
- MLOps / Experto: probar Docker, tests y scripts expertos.
- QA / Docs: cerrar informe, README, capturas y presentaciones.

### Entregables

- Repo ordenado.
- Informe tecnico.
- Presentacion de negocio.
- Presentacion tecnica.
- Enlace a Jira.
- Demo final.

### Verificacion

- Checklist de consigna completo.
- App ejecutable.
- Overfitting inferior al 5% demostrado.
- Metricas explicadas.
- Presentaciones alineadas con el sistema real.

### Riesgos

- Ultimos cambios rompen la demo.
- Presentacion promete mas que el codigo.
- Falta evidencia de comandos o capturas.
