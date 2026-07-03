# SPEC 1 - Intent

## Proposito del proyecto

Este proyecto grupal busca construir una solucion de Machine Learning para un problema de clasificacion supervisada. La entrega debe incluir un modelo capaz de recibir datos de entrada, devolver una prediccion de clase y explicar su rendimiento con metricas tecnicas claras.

El proyecto debe proteger primero el Nivel Esencial exigido por la consigna y, despues, sumar una capa incremental de Nivel Medio, Avanzado y Experto cuando el nucleo ya sea estable.

## Problema que se quiere resolver

El cliente del proyecto es una plataforma de reservas hoteleras similar a Booking, Trivago o Agoda. El problema de negocio consiste en anticipar si una reserva sera cancelada o no, para ayudar a gestionar disponibilidad, ocupacion, ingresos y planificacion operativa.

El problema debe poder formularse asi:

- Dado un conjunto de variables de entrada, el sistema predice una variable objetivo categorica.
- La prediccion debe ser util para una decision concreta.
- La calidad del modelo debe poder medirse con datos de validacion y metricas de clasificacion.

En este proyecto, el sistema buscara predecir el estado de una reserva a partir de informacion disponible antes de la fecha de llegada.

## Por que usamos metodologia SPEC

SPEC se usara como contrato comun del equipo. Su funcion es evitar que el proyecto dependa de decisiones improvisadas o de trabajo aislado.

La carpeta `.specify/` define:

- Que se va a construir.
- Que queda fuera de alcance.
- Como se decide si algo esta bien hecho.
- Que tareas corresponden a cada frente de trabajo.
- Que evidencia debe existir antes de considerar cerrada una fase.

Si una tarea, rama, notebook, script o decision contradice esta especificacion, se debe corregir la tarea o actualizar la especificacion de forma explicita.

## Objetivo protegido: Nivel Esencial

El equipo debe asegurar una entrega esencial solida antes de depender de componentes avanzados.

El Nivel Esencial queda protegido cuando existe:

- Dataset cargado y documentado.
- Target definido.
- EDA con visualizaciones relevantes para clasificacion.
- Preprocesamiento reproducible.
- Modelo baseline funcional.
- Metricas de clasificacion calculadas.
- Overfitting inferior al 5%.
- Aplicacion productivizada que recibe datos y devuelve prediccion.
- Informe tecnico con interpretacion del rendimiento.
- README con instalacion, ejecucion y estructura del proyecto.

Ninguna tarea experta debe bloquear la entrega esencial.

## Objetivo aspiracional: Nivel Experto

Cuando el nucleo esencial sea verificable, el equipo aspirara a construir una capa experta con:

- Red neuronal experimental o desplegable.
- Sistema Champion/Challenger.
- A/B Testing para comparar modelos.
- Monitoreo de Data Drift.
- Auto-reemplazo de modelos condicionado por metricas predefinidas.

La capa experta debe ser incremental. Si no mejora el sistema esencial, se documentara como experimento comparativo.

## Principios de trabajo del equipo

- Priorizar primero una entrega minima ejecutable.
- Trabajar en paralelo por frentes permanentes.
- Mantener ramas limpias y commits descriptivos.
- Evitar notebooks o scripts sin trazabilidad.
- Documentar decisiones tecnicas relevantes.
- Verificar cada entrega con comandos, capturas o evidencia reproducible.
- No mezclar cambios de produccion con cambios de planificacion.
- Mantener el README y Trello alineados con el estado real.

## Manejo de distintos niveles tecnicos

El equipo tiene 4 integrantes y uno tiene nivel tecnico muy bajo. La planificacion debe darle tareas utiles, continuas y verificables, sin hacerlo responsable unico de componentes criticos.

Distribucion sugerida:

- Integrante 1 - ML Core: dataset, EDA, preprocessing, baseline, ensemble y Champion Model.
- Integrante 2 - App / Producto: app, formulario, prediccion, feedback, almacenamiento y dashboard simple.
- Integrante 3 - MLOps / Experto: Docker, tests tecnicos, red neuronal, A/B Testing, drift y auto-reemplazo.
- Integrante 4 - QA / Docs / Presentacion: Trello, README, checklist, tabla de experimentos, capturas, validacion manual, presentacion de negocio y apoyo en interpretacion de metricas.

El integrante junior puede ejecutar tareas guiadas con criterios de verificacion claros. No debe ser responsable unico de:

- Modelo final.
- App productiva.
- Preprocesamiento critico.
- Data Drift.
- Auto-reemplazo.
- Despliegue.

## Estado deseado al finalizar

Al final del proyecto, el repositorio debe permitir:

- Instalar dependencias.
- Ejecutar la app.
- Reproducir el entrenamiento o explicar como se genero el modelo.
- Consultar metricas y evidencia del rendimiento.
- Ver el modelo Champion seleccionado.
- Registrar feedback o nuevos datos.
- Ejecutar tests minimos.
- Levantar el sistema con Docker, si se alcanza Nivel Avanzado.
- Mostrar una demo clara para negocio y una explicacion tecnica del codigo.

## Audiencia del documento

Este documento esta dirigido a:

- Integrantes del equipo.
- Docentes o evaluadores.
- Agentes de IA que colaboren en el repositorio.
- Cualquier persona que necesite entender el alcance antes de programar.

La regla principal es simple: primero una entrega esencial estable, despues mejoras incrementales.
