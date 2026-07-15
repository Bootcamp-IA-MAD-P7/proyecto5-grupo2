# Database Migrations

## Objetivo

Versionar todos los cambios de esquema de Hotel Insights y aplicar la misma secuencia en SQLite local y PostgreSQL de AWS.

La aplicacion utiliza Alembic `1.18.5`. La revision actual es:

```text
0001_prediction_feedback
```

## Politica

- Cada cambio de tablas, columnas, indices o restricciones requiere una nueva revision.
- Las migraciones se revisan y prueban antes de mergear a `develop`.
- FastAPI no crea tablas mediante `Base.metadata.create_all()` durante el arranque.
- La API solo arranca cuando `alembic upgrade head` termina correctamente.
- Nunca se modifica una revision que ya fue aplicada en AWS; se crea una revision posterior.
- Un downgrade en produccion requiere copia de seguridad y aprobacion explicita.

## Uso local sin Docker

Aplicar todas las migraciones:

```bash
python -m alembic upgrade head
```

Consultar la revision instalada:

```bash
python -m alembic current
```

Revertir una revision, solo tras copia de seguridad y revision del impacto:

```bash
python -m alembic downgrade -1
```

Comprobar si los modelos SQLAlchemy requieren otra migracion:

```bash
python -m alembic check
```

## Docker y AWS

`scripts/start_backend.sh` ejecuta:

```bash
alembic upgrade head
```

Solo despues inicia Uvicorn. Este mismo script se usa en Docker Compose local y en EC2. Si la migracion falla, el contenedor backend no queda saludable y el despliegue automatico falla sin publicar una API con un esquema incompatible.

## Adopcion de la base existente

La revision inicial contempla la tabla `prediction_feedback` que existia antes de introducir Alembic:

1. Si la tabla no existe, la crea con sus indices.
2. Si existe y todas sus columnas coinciden, conserva los registros y adopta el esquema.
3. Si faltan o sobran columnas, detiene la migracion y muestra la diferencia.

La migracion no elimina datos durante esta adopcion.

## Crear una nueva revision

Despues de modificar los modelos SQLAlchemy:

```bash
python -m alembic revision --autogenerate -m "describe schema change"
```

La revision generada debe revisarse manualmente. Antes del PR:

```bash
python -m alembic upgrade head
python -m alembic check
python -m pytest
```

## Verificacion

Las pruebas automatizadas estan en:

```text
tests/unit/test_database_migrations.py
```

Cubren:

- Creacion de una base nueva.
- Conservacion de registros de una base anterior.
- Rechazo de un esquema incompatible.
- Registro de la revision en `alembic_version`.
- Reversion controlada sobre una base temporal.
