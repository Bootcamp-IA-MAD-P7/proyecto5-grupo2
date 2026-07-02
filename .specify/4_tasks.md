# SPEC 4 - Tasks

Este backlog puede pasarse a Trello, Jira, Notion o GitHub Projects. Cada ticket debe moverse de estado solo cuando su criterio de verificacion este cumplido.

## Protocolo de ejecucion

1. Antes de empezar un ticket, revisar dependencias.
2. Crear o usar una rama con nombre descriptivo.
3. Tocar solo los archivos indicados o actualizar el ticket si cambia el alcance.
4. Registrar evidencia de verificacion.
5. Actualizar README, informe o tabla de experimentos si el cambio afecta al uso del proyecto.
6. Pedir revision tecnica en tickets criticos.

## Leyenda de estados

- `[ ]` pendiente.
- `[~]` en progreso.
- `[x]` completada y verificada.
- `[!]` bloqueada.
- `[-]` cancelada/no aplica.

## Roles sugeridos

- I1 - ML Core.
- I2 - App / Producto.
- I3 - MLOps / Experto.
- I4 - QA / Docs / Presentacion, integrante junior con tareas guiadas.

## Fase 0 - Preparacion

### [ ] T-0.1 Crear tablero de gestion

- Archivos afectados: ninguno o `README.md` si se agrega enlace.
- Accion: crear Trello o herramienta equivalente con columnas Backlog, In Progress, Review, Done y Blocked.
- Responsable sugerido: I4.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: ninguna.
- Criterio de verificacion: tablero creado con tickets iniciales.
- Comando de verificacion: no aplica.

### [ ] T-0.2 Revisar y aceptar SPEC inicial

- Archivos afectados: `.specify/`.
- Accion: leer los cuatro documentos SPEC y anotar dudas o cambios.
- Responsable sugerido: todo el equipo, coordinado por I4.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: `.specify/` creado.
- Criterio de verificacion: acuerdos registrados y TODO principales identificados.
- Comando de verificacion: no aplica.

### [ ] T-0.3 Definir candidatos de dataset

- Archivos afectados: `.specify/2_spec.md`, `README.md`.
- Accion: listar 2 o 3 datasets candidatos con target posible, fuente, ventajas y riesgos.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: con apoyo.
- Dependencias: T-0.2.
- Criterio de verificacion: el equipo puede elegir dataset con criterios claros.
- Comando de verificacion: no aplica.

### [ ] T-0.4 Disenar mock funcional de app

- Archivos afectados: `docs/` o tablero.
- Accion: definir pantallas minimas de app: formulario, resultado, feedback y version de modelo.
- Responsable sugerido: I2.
- Dificultad: baja.
- Apto junior: con apoyo visual.
- Dependencias: T-0.3 parcial.
- Criterio de verificacion: flujo de app entendido por todo el equipo.
- Comando de verificacion: no aplica.

## Fase 1 - Dataset y EDA

### [ ] T-1.1 Elegir dataset definitivo

- Archivos afectados: `.specify/2_spec.md`, `README.md`, `data/raw/` si aplica.
- Accion: seleccionar dataset, documentar fuente y forma de descarga.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-0.3.
- Criterio de verificacion: dataset accesible y target posible.
- Comando de verificacion: TODO: definir cuando exista estructura del proyecto.

### [ ] T-1.2 Definir target y clases

- Archivos afectados: `.specify/2_spec.md`, `reports/model_report.md`.
- Accion: documentar columna target, clases, distribucion y posible desbalance.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: con apoyo en documentacion.
- Dependencias: T-1.1.
- Criterio de verificacion: target aceptado por el equipo.
- Comando de verificacion: TODO.

### [ ] T-1.3 Crear diccionario de datos

- Archivos afectados: `reports/`, `README.md`.
- Accion: listar columnas, tipo de dato, descripcion, rol y si entra al modelo.
- Responsable sugerido: I4 con revision de I1.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-1.1.
- Criterio de verificacion: todas las columnas relevantes estan clasificadas.
- Comando de verificacion: no aplica.

### [ ] T-1.4 Realizar EDA inicial

- Archivos afectados: `notebooks/`, `reports/figures/`, `reports/model_report.md`.
- Accion: analizar nulos, duplicados, distribuciones, target, correlaciones y relaciones con target.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-1.1, T-1.2.
- Criterio de verificacion: existen graficos relevantes para clasificacion.
- Comando de verificacion: TODO.

### [ ] T-1.5 Interpretar graficos para negocio

- Archivos afectados: `reports/model_report.md`, `docs/business_presentation/`.
- Accion: escribir interpretaciones simples de los graficos principales.
- Responsable sugerido: I4 con revision de I1.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-1.4.
- Criterio de verificacion: cada grafico usado en presentacion tiene una lectura clara.
- Comando de verificacion: no aplica.

## Fase 2 - Nivel Esencial MVP

### [ ] T-2.1 Crear pipeline de preprocesamiento

- Archivos afectados: `src/features/`, `src/models/`.
- Accion: construir transformaciones para numericas, categoricas y columnas excluidas.
- Responsable sugerido: I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-1.2, T-1.3.
- Criterio de verificacion: el pipeline transforma train y validacion sin errores ni leakage.
- Comando de verificacion: TODO: `python -m pytest` cuando existan tests.

### [ ] T-2.2 Entrenar baseline

- Archivos afectados: `src/models/`, `models/`, `reports/model_report.md`.
- Accion: entrenar modelo simple y guardar metricas train-validacion.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-2.1.
- Criterio de verificacion: baseline registrado en tabla de experimentos.
- Comando de verificacion: TODO.

### [ ] T-2.3 Calcular metricas obligatorias

- Archivos afectados: `src/evaluation/`, `reports/model_report.md`, `reports/figures/`.
- Accion: calcular accuracy, precision, recall, F1, ROC-AUC, matriz de confusion y curva ROC si aplica.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: con apoyo para documentar resultados.
- Dependencias: T-2.2.
- Criterio de verificacion: metricas visibles en informe.
- Comando de verificacion: TODO.

### [ ] T-2.4 Revisar overfitting inferior al 5%

- Archivos afectados: `reports/model_report.md`, tabla de experimentos.
- Accion: comparar metrica principal en train y validacion.
- Responsable sugerido: I1 con QA de I4.
- Dificultad: media.
- Apto junior: si para checklist, no para decision tecnica final.
- Dependencias: T-2.3.
- Criterio de verificacion: diferencia < 0.05 o bloqueo documentado.
- Comando de verificacion: TODO.

### [ ] T-2.5 Crear app minima de prediccion

- Archivos afectados: `app/`, `README.md`.
- Accion: crear formulario, cargar modelo y devolver prediccion.
- Responsable sugerido: I2.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-2.2.
- Criterio de verificacion: usuario puede ingresar datos y obtener clase predicha.
- Comando de verificacion: TODO: comando de ejecucion de app.

### [ ] T-2.6 Validacion manual de app

- Archivos afectados: `docs/`, `reports/`, `README.md`.
- Accion: probar 5 entradas manuales, tomar capturas y registrar resultados.
- Responsable sugerido: I4.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-2.5.
- Criterio de verificacion: capturas y checklist de validacion completos.
- Comando de verificacion: no aplica.

## Fase 3 - Nivel Medio

### [ ] T-3.1 Entrenar modelo ensemble

- Archivos afectados: `src/models/`, `models/`, `reports/model_report.md`.
- Accion: entrenar Random Forest, Gradient Boosting u otro ensemble justificado.
- Responsable sugerido: I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-2.1, T-2.3.
- Criterio de verificacion: ensemble comparado contra baseline.
- Comando de verificacion: TODO.

### [ ] T-3.2 Aplicar validacion cruzada

- Archivos afectados: `src/models/`, `reports/model_report.md`.
- Accion: ejecutar K-Fold o estrategia equivalente y reportar promedio/desviacion.
- Responsable sugerido: I1.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-3.1.
- Criterio de verificacion: resultados de CV documentados.
- Comando de verificacion: TODO.

### [ ] T-3.3 Optimizar hiperparametros

- Archivos afectados: `src/models/`, `reports/model_report.md`.
- Accion: usar GridSearch, RandomSearch u Optuna si se justifica.
- Responsable sugerido: I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.2.
- Criterio de verificacion: mejores parametros y comparacion documentados.
- Comando de verificacion: TODO.

### [ ] T-3.4 Seleccionar Champion Model

- Archivos afectados: `models/champion/`, `reports/model_report.md`, `.specify/2_spec.md`.
- Accion: elegir modelo final segun metricas, overfitting, estabilidad e integracion con app.
- Responsable sugerido: I1 con revision de I2 e I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.3, T-2.5.
- Criterio de verificacion: Champion versionado y explicado.
- Comando de verificacion: TODO.

### [ ] T-3.5 Crear tabla de experimentos

- Archivos afectados: `reports/`, `README.md`.
- Accion: registrar modelo, parametros, metricas train/validacion, overfitting y decision.
- Responsable sugerido: I4 con revision de I1.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-2.2.
- Criterio de verificacion: todos los modelos probados aparecen en la tabla.
- Comando de verificacion: no aplica.

### [ ] T-3.6 Implementar feedback

- Archivos afectados: `app/`, `data/feedback/`, `src/data/`.
- Accion: guardar feedback de usuario y predicciones para futuro reentrenamiento.
- Responsable sugerido: I2.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-2.5.
- Criterio de verificacion: feedback queda persistido y se puede abrir.
- Comando de verificacion: TODO.

## Fase 4 - Nivel Avanzado

### [ ] T-4.1 Crear tests minimos de preprocessing

- Archivos afectados: `tests/`, `src/features/`.
- Accion: validar que el pipeline procesa datos validos y rechaza datos invalidos controlados.
- Responsable sugerido: I3.
- Dificultad: media.
- Apto junior: con guia para casos simples.
- Dependencias: T-2.1.
- Criterio de verificacion: tests pasan.
- Comando de verificacion: `python -m pytest`

### [ ] T-4.2 Crear tests minimos de metricas

- Archivos afectados: `tests/`, `src/evaluation/`.
- Accion: testear umbral minimo y regla de overfitting.
- Responsable sugerido: I3.
- Dificultad: media.
- Apto junior: con guia.
- Dependencias: T-2.3, T-2.4.
- Criterio de verificacion: tests pasan y fallan si la regla se incumple.
- Comando de verificacion: `python -m pytest`

### [ ] T-4.3 Dockerizar app

- Archivos afectados: `Dockerfile`, `docker-compose.yml`, `README.md`.
- Accion: crear imagen que levante la app y cargue el modelo Champion.
- Responsable sugerido: I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-2.5, T-3.4.
- Criterio de verificacion: app levanta con Docker.
- Comando de verificacion: TODO: `docker build` y `docker run` cuando exista app.

### [ ] T-4.4 Conectar almacenamiento persistente

- Archivos afectados: `app/`, `src/data/`, `data/feedback/`.
- Accion: usar CSV, SQLite o base de datos para predicciones y feedback.
- Responsable sugerido: I2 con apoyo de I3.
- Dificultad: media.
- Apto junior: no como responsable unico.
- Dependencias: T-3.6.
- Criterio de verificacion: datos persisten tras reiniciar app.
- Comando de verificacion: TODO.

### [ ] T-4.5 Documentar instalacion y ejecucion

- Archivos afectados: `README.md`.
- Accion: escribir pasos para entorno local, app, tests y Docker.
- Responsable sugerido: I4 con revision de I2 e I3.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: T-2.5, T-4.3.
- Criterio de verificacion: otra persona puede seguir el README.
- Comando de verificacion: ejecutar comandos documentados.

## Fase 5 - Nivel Experto

### [ ] T-5.1 Entrenar red neuronal experimental

- Archivos afectados: `src/models/`, `models/challengers/`, `reports/model_report.md`.
- Accion: entrenar red neuronal comparable contra Champion.
- Responsable sugerido: I3 con apoyo de I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.4.
- Criterio de verificacion: metricas comparables documentadas.
- Comando de verificacion: TODO.

### [ ] T-5.2 Implementar o simular A/B Testing

- Archivos afectados: `src/mlops/`, `app/`, `reports/model_report.md`.
- Accion: enrutar o simular trafico entre Champion y Challenger registrando `model_version`.
- Responsable sugerido: I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.4, T-5.1.
- Criterio de verificacion: comparacion Champion vs Challenger reproducible.
- Comando de verificacion: TODO.

### [ ] T-5.3 Medir Data Drift

- Archivos afectados: `src/mlops/`, `reports/`, `data/feedback/`.
- Accion: calcular PSI, KS Test o metodo equivalente entre entrenamiento y datos nuevos.
- Responsable sugerido: I3.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-3.6.
- Criterio de verificacion: reporte de drift con umbrales.
- Comando de verificacion: TODO.

### [ ] T-5.4 Auto-reemplazo condicionado

- Archivos afectados: `src/mlops/`, `models/`, `reports/model_report.md`.
- Accion: crear logica que promueva un Challenger solo si supera reglas de metricas y overfitting.
- Responsable sugerido: I3 con revision de I1.
- Dificultad: alta.
- Apto junior: no.
- Dependencias: T-5.2, T-5.3.
- Criterio de verificacion: un modelo inferior no reemplaza al Champion en prueba controlada.
- Comando de verificacion: TODO.

### [ ] T-5.5 Documentar ciclo MLOps para defensa

- Archivos afectados: `docs/technical_presentation/`, `reports/model_report.md`.
- Accion: explicar Champion/Challenger, A/B, drift y auto-reemplazo con diagrama simple.
- Responsable sugerido: I4 con revision de I3.
- Dificultad: media.
- Apto junior: si con plantilla.
- Dependencias: T-5.2, T-5.3, T-5.4.
- Criterio de verificacion: la presentacion explica reglas y limitaciones sin prometer mas de lo implementado.
- Comando de verificacion: no aplica.

## Fase 6 - Cierre

### [ ] T-6.1 Smoke test completo

- Archivos afectados: `reports/`, `README.md`.
- Accion: ejecutar app, cargar modelo, hacer prediccion, guardar feedback y revisar salida.
- Responsable sugerido: I2 e I4.
- Dificultad: baja.
- Apto junior: si para validacion manual.
- Dependencias: T-2.5, T-3.6.
- Criterio de verificacion: checklist de demo completo.
- Comando de verificacion: TODO: comando final de app.

### [ ] T-6.2 Revision final de overfitting y metricas

- Archivos afectados: `reports/model_report.md`, `docs/technical_presentation/`.
- Accion: revisar que metricas finales coincidan con informe, README y presentacion.
- Responsable sugerido: I1 con QA de I4.
- Dificultad: media.
- Apto junior: si para checklist, no para decision tecnica.
- Dependencias: T-3.4.
- Criterio de verificacion: overfitting < 5% demostrado y sin contradicciones.
- Comando de verificacion: TODO.

### [ ] T-6.3 Preparar presentacion de negocio

- Archivos afectados: `docs/business_presentation/`.
- Accion: preparar narrativa, problema, solucion, demo, impacto y limitaciones.
- Responsable sugerido: I4 con apoyo de todo el equipo.
- Dificultad: media.
- Apto junior: si.
- Dependencias: T-1.5, T-2.6.
- Criterio de verificacion: presentacion no contiene tecnicismos innecesarios y usa capturas reales.
- Comando de verificacion: no aplica.

### [ ] T-6.4 Preparar presentacion tecnica

- Archivos afectados: `docs/technical_presentation/`.
- Accion: explicar estructura, preprocessing, modelos, metricas, app, Docker y MLOps si aplica.
- Responsable sugerido: I1, I2 e I3, coordinado por I4.
- Dificultad: media.
- Apto junior: si como coordinacion y formato.
- Dependencias: T-3.4, T-4.3, T-5.5.
- Criterio de verificacion: cada decision tecnica importante tiene evidencia.
- Comando de verificacion: no aplica.

### [ ] T-6.5 Checklist final de consigna

- Archivos afectados: `README.md`, `reports/`, `.specify/4_tasks.md`.
- Accion: revisar app, GitHub, informe, presentaciones, Trello, Docker, tests y niveles alcanzados.
- Responsable sugerido: I4 con revision de todo el equipo.
- Dificultad: baja.
- Apto junior: si.
- Dependencias: todas las tareas de cierre.
- Criterio de verificacion: no quedan requisitos obligatorios sin evidencia.
- Comando de verificacion: no aplica.
