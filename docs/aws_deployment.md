# AWS Deployment - Hotel Insights

## 1. Objetivo

Esta guía documenta el despliegue operativo de Hotel Insights en AWS. La misma aplicación se ejecuta en local y en AWS mediante Docker; no existen implementaciones funcionales separadas.

URL pública estable:

```text
https://d3lxpalnzir74p.cloudfront.net
https://d3lxpalnzir74p.cloudfront.net/monitoring
```

## 2. Arquitectura desplegada

```text
Usuario
  |
  v
Amazon CloudFront (HTTPS)
  |
  v
Amazon EC2 (Docker Compose)
  |-- nginx + frontend React
  |-- FastAPI + Champion Random Forest
  |
  v
Amazon RDS for PostgreSQL
```

Componentes:

- **CloudFront** proporciona la URL HTTPS pública y reenvía todos los métodos HTTP necesarios.
- **EC2** ejecuta frontend y backend con `docker-compose.ec2.yml`.
- **nginx** sirve la SPA y envía las solicitudes `/api/` al backend dentro de la red Docker.
- **FastAPI** carga `random_forest_champion_v0.1.0`, expone inferencia y registra feedback.
- **Alembic** aplica las migraciones pendientes antes de que el contenedor backend inicie FastAPI.
- **RDS PostgreSQL** persiste feedback y resultados operativos fuera del ciclo de vida de los contenedores.
- **GitHub Actions** despliega automáticamente cada merge en `develop` mediante OIDC y AWS Systems Manager.

La configuración antigua de AWS App Runner se retiró del repositorio para evitar rutas de despliegue ambiguas. La arquitectura vigente es CloudFront + EC2 + RDS.

## 3. Configuración de ejecución

La instancia EC2 mantiene un archivo privado `.env.ec2`, ignorado por Git, creado a partir de `.env.ec2.example`:

```text
DATABASE_URL=postgresql://DB_USER:URL_ENCODED_PASSWORD@RDS_ENDPOINT:5432/postgres
CORS_ORIGINS=https://CLOUDFRONT_DOMAIN
```

Reglas:

- Nunca subir `.env.ec2`, contraseñas, endpoints privados ni credenciales al repositorio.
- La contraseña incluida en `DATABASE_URL` debe codificarse para URL cuando contenga caracteres reservados.
- El backend queda accesible solo dentro de la red Docker; el único puerto público de EC2 es el `80` de nginx.

## 4. Despliegue manual en EC2

Desde `/home/ubuntu/hotel-insights`:

```bash
git switch develop
git pull --ff-only origin develop
bash scripts/deploy_ec2.sh
```

El script:

1. Comprueba que existe `.env.ec2`.
2. Valida la configuración de Docker Compose.
3. Reconstruye y levanta los contenedores.
4. El backend ejecuta `alembic upgrade head`; si falla, FastAPI no arranca.
5. Espera a que `GET /api/health/ready` confirme Champion y base de datos.
6. Comprueba `GET /api/model/info`.
7. Muestra el estado de los servicios y limpia imágenes no utilizadas.

## 5. Despliegue automático

El workflow `.github/workflows/deploy-aws-ec2.yml` se ejecuta tras cada `push` a `develop` y también permite ejecución manual.

Flujo:

1. GitHub ejecuta la suite Python completa y el build frontend como quality gates reutilizables.
2. El despliegue solo continúa si ambos jobs terminan correctamente.
3. GitHub solicita credenciales temporales de AWS mediante OIDC.
4. GitHub Actions asume un rol IAM sin almacenar claves de acceso permanentes.
5. AWS Systems Manager envía el comando de despliegue a EC2.
6. EC2 actualiza `develop` con `--ff-only` y ejecuta `scripts/deploy_ec2.sh`.
7. El workflow espera el resultado y falla si el despliegue o el readiness check no terminan correctamente.

Variables de repositorio requeridas:

```text
AWS_DEPLOY_ROLE_ARN
AWS_REGION
EC2_INSTANCE_ID
```

No se necesitan claves `AWS_ACCESS_KEY_ID` ni `AWS_SECRET_ACCESS_KEY` en GitHub.

## 6. Seguridad aplicada

- RDS no es accesible públicamente.
- El puerto PostgreSQL `5432` solo admite tráfico desde el grupo de seguridad de EC2.
- SSH `22` está limitado a la IP autorizada para administración.
- HTTP `80` en EC2 solo admite tráfico desde la lista administrada de orígenes de CloudFront.
- Los usuarios acceden mediante HTTPS en CloudFront.
- Las credenciales de base de datos permanecen únicamente en `.env.ec2` con permisos restringidos.
- El rol de despliegue de GitHub se limita al repositorio, a `develop` y a la instancia etiquetada para la aplicación.

## 7. Verificación operativa

Comprobaciones públicas:

```text
GET https://d3lxpalnzir74p.cloudfront.net/
GET https://d3lxpalnzir74p.cloudfront.net/monitoring
GET https://d3lxpalnzir74p.cloudfront.net/api/health
GET https://d3lxpalnzir74p.cloudfront.net/api/health/ready
GET https://d3lxpalnzir74p.cloudfront.net/api/model/info
GET https://d3lxpalnzir74p.cloudfront.net/api/feedback/summary
GET https://d3lxpalnzir74p.cloudfront.net/api/monitoring/experiments
GET https://d3lxpalnzir74p.cloudfront.net/api/reservations/demo?limit=4&offset=4
```

Resultado validado el 14 de julio de 2026:

- Frontend accesible desde escritorio y móvil.
- API disponible y readiness confirmado con Champion y PostgreSQL.
- Champion `random_forest_champion_v0.1.0` cargado.
- Persistencia identificada como `postgresql`.
- Feedback conservado después de reiniciar el backend.
- Esquema gestionado por Alembic; el despliegue aplica `0002_prediction_logs` antes de iniciar la API.
- Despliegue automático desde `develop` completado correctamente.
- Acceso HTTP directo a la IP de EC2 bloqueado después de restringir el origen a CloudFront.

Validación final del commit `d752892` el 16 de julio de 2026:

- 76 tests Python superados y build de frontend completado.
- Stack Docker completo saludable con readiness de Champion y PostgreSQL.
- Aplicación de negocio definitiva, dashboard `/monitoring`, readiness y metadatos del Champion disponibles públicamente con respuesta `200 OK`.
- Página `Modelo` publicada con cifras contrastadas contra el CSV y los artefactos del Champion.
- Auditorías de dependencias Python y frontend sin vulnerabilidades conocidas.

## 8. Diagnóstico

En EC2:

```bash
docker compose --env-file .env.ec2 -f docker-compose.ec2.yml ps
docker compose --env-file .env.ec2 -f docker-compose.ec2.yml logs --tail=100
curl --fail http://localhost/api/health
curl --fail http://localhost/api/health/ready
curl --fail http://localhost/api/model/info
curl --fail http://localhost/api/feedback/summary
```

Los logs del backend se emiten como eventos JSON e incluyen `request_id`, metodo, ruta, estado y duracion. Los eventos de inferencia añaden `prediction_id` y version del modelo. No se registran payloads ni credenciales. Consulte `docs/observability.md` para el contrato operativo.

En GitHub:

- Revisar `Actions > Deploy to AWS EC2`.
- Comprobar el resultado del comando SSM.
- No repetir el despliegue manualmente hasta conocer la causa de un fallo.

## 9. Actualización y retirada

Para publicar cambios, se mantiene el flujo habitual:

```text
rama de trabajo -> Pull Request -> revisión -> merge en develop -> despliegue automático
```

Cuando termine la demostración temporal, los recursos deben retirarse en orden controlado para evitar costes residuales:

1. Deshabilitar el workflow de despliegue.
2. Eliminar la distribución CloudFront cuando ya no se necesite.
3. Detener o terminar EC2 y liberar su Elastic IP.
4. Crear una copia final solo si es necesaria y eliminar RDS.
5. Revisar volúmenes, snapshots y otros recursos facturables.
6. Confirmar el cierre en AWS Cost Explorer o Billing.
