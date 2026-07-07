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

Plantilla mínima:

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

## 9. Tags

Los tags se usarán solo para hitos importantes.

Ejemplos:

```text
v0.1.0-spec
v0.2.0-eda
v0.3.0-frontend
v0.4.0-baseline
v0.5.0-api
v0.6.0-champion
v1.0.0-final
```

Crear tag:

```bash
git tag -a v0.3.0-frontend -m "Frontend React integrated"
git push origin v0.3.0-frontend
```

No se deben crear tags sin acuerdo del equipo.

## 10. Flujo recomendado para este proyecto

El flujo ideal será:

```text
feature/... -> Pull Request -> develop -> release/tag -> main
```

`main` queda protegida para entregas estables.

`develop` concentra el trabajo integrado.

Las ramas feature permiten revisar cambios sin interferir con el resto del equipo.