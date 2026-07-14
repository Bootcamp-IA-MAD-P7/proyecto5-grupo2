# Git Workflow - Hotel Insights

## 1. Objetivo

Este documento define cómo debe trabajar el equipo con Git y GitHub para evitar conflictos, proteger la rama principal y mantener un historial limpio.

El objetivo es trabajar como en un proyecto real de software: ramas pequeñas, Pull Requests revisables y commits descriptivos.

## 2. Ramas principales

El repositorio tendrá dos ramas principales:

```text
main
develop
```

### main

`main` representa la versión estable del proyecto.

Reglas:

- No se trabaja directamente sobre `main`.
- No se suben commits directos.
- Solo debe recibir merges desde `develop` cuando haya una versión estable o entrega importante.
- Puede usarse para tags finales o releases.

### develop

`develop` es la rama de integración del equipo.

Reglas:

- Todo el trabajo debe integrarse aquí mediante Pull Request.
- Debe mantenerse ejecutable.
- No se recomienda trabajar directamente sobre `develop`.
- Antes de crear una rama nueva, siempre se debe actualizar desde `develop`.

## 3. Ramas de trabajo

Cada tarea debe hacerse en una rama separada.

Convenciones recomendadas:

```text
feature/nombre-tarea
docs/nombre-documento
fix/nombre-error
test/nombre-test
chore/nombre-mantenimiento
```

Ejemplos:

```text
feature/ml-baseline
feature/backend-predict-api
feature/app-feedback
docs/readme-installation
docs/project-organization-proposal
fix/frontend-navbar-layout
test/preprocessing-pipeline
chore/update-gitignore
```

## 4. Flujo recomendado

Antes de empezar una tarea:

```bash
git switch develop
git pull origin develop
git switch -c feature/nombre-tarea
```

Trabajar, guardar cambios y revisar estado:

```bash
git status
```

Añadir solo los archivos necesarios:

```bash
git add ruta/del/archivo
```

Crear commit:

```bash
git commit -m "tipo: descripcion corta"
```

Subir rama:

```bash
git push -u origin feature/nombre-tarea
```

Crear Pull Request en GitHub:

```text
base: develop
compare: feature/nombre-tarea
```

## 5. Tipos de commits

Usaremos mensajes simples inspirados en Conventional Commits.

Tipos recomendados:

```text
feat: nueva funcionalidad
fix: corrección de error
docs: documentación
test: tests
refactor: reestructuración sin cambio funcional
chore: mantenimiento
style: cambios visuales o formato
ci: GitHub Actions o automatización
```

Ejemplos:

```text
feat: add baseline training pipeline
docs: add project vision
fix: correct frontend menu spacing
test: add preprocessing schema tests
ci: add frontend build workflow
```

## 6. Pull Requests

Cada PR debe incluir:

- Qué cambia.
- Qué tarea SPEC avanza.
- Cómo se ha verificado.
- Qué queda pendiente.

El repositorio incluye una plantilla automatica en:

```text
.github/pull_request_template.md
```

GitHub la muestra al crear un Pull Request cuando la rama base existe en la rama por defecto del repositorio. Durante el desarrollo, la rama por defecto recomendada es `develop`.

Plantilla minima esperada:

```markdown
## Summary

-

## SPEC task

-

## Verification

-

## Pending

-
```

## 7. Qué no hacer

Evitar:

- Trabajar directamente en `main`.
- Trabajar directamente en `develop` salvo cambios mínimos acordados.
- Mezclar frontend, ML, documentación y Docker en un único PR grande.
- Subir `node_modules/`, `dist/`, `.venv/`, `.env` o datasets generados pesados.
- Hacer commits con mensajes como `cambios`, `update`, `cosas`, `final final`.

## 8. Sincronizar una rama de trabajo

Si `develop` avanza mientras se trabaja en una rama:

```bash
git fetch origin
git switch feature/nombre-tarea
git merge origin/develop
```

Si hay conflictos, se resuelven localmente y se hace commit del merge.

Para el equipo, `merge` es más fácil de entender que `rebase`.

## 9. Changelog

El repositorio incluye:

```text
CHANGELOG.md
```

El changelog sirve para explicar los hitos del proyecto en lenguaje claro. No es automatico: se actualiza cuando el equipo cierra una fase relevante o crea una version.

Uso recomendado:

- Antes de crear un tag, actualizar `CHANGELOG.md`.
- Agrupar cambios por version o hito.
- Mantener una seccion `Unreleased` para lo que esta integrado en `develop` pero aun no tiene version.
- No duplicar todos los commits; el changelog resume valor entregado.

## 10. Tags

Los tags se usarán solo para hitos importantes.

Tags ya creados:

```text
v0.1.0-docs-foundation
v0.2.0-frontend-mock
v0.4.0-essential-mvp
v0.5.0-operational-mvp
v0.6.0-aws-deployment
```

Siguiente tag previsto:

```text
v1.0.0-final
```

Crear tag:

```bash
git tag -a v0.4.0-essential-mvp -m "Essential MVP milestone"
git push origin v0.4.0-essential-mvp
```

No se deben crear tags sin acuerdo del equipo.

## 11. Flujo recomendado para este proyecto

El flujo ideal será:

```text
feature/... -> Pull Request -> develop -> release/tag -> main
```

`main` queda protegida para entregas estables.

`develop` concentra el trabajo integrado.

Durante el desarrollo del proyecto, `develop` puede configurarse como rama por defecto en GitHub para que los Pull Requests se creen contra la rama correcta por defecto. Esto no sustituye a `main`: solo cambia la rama que GitHub muestra primero. Al final del proyecto, cuando `develop` este validada, se hara un merge controlado hacia `main`.

Las ramas feature permiten revisar cambios sin interferir con el resto del equipo.

## 12. CI/CD y despliegue desde develop

Los Pull Requests ejecutan comprobaciones automáticas de backend y frontend. Después del merge, cada `push` a `develop` activa también el workflow de despliegue AWS.

```text
rama -> PR -> checks CI -> merge en develop -> despliegue AWS -> health check
```

Reglas:

- No mergear si fallan los checks obligatorios.
- No hacer `push` directo a `develop` para evitar despliegues sin revisión.
- GitHub usa OIDC para obtener credenciales temporales de AWS; no se guardan claves permanentes.
- AWS Systems Manager ejecuta el despliegue en EC2.
- El workflow falla si el script no levanta los contenedores o la API no supera el health check.
- Un cambio documental también activa el despliegue porque el trigger actual es cualquier `push` a `develop`; esta optimización puede abordarse después de la entrega.

Guía operativa: `docs/aws_deployment.md`.
