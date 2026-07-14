# AWS Deployment - Hotel Insights

## 1. Objetivo

Esta guía documenta el despliegue operativo de Hotel Insights en AWS. La misma aplicación se ejecuta en local y en AWS mediante Docker; no existen implementaciones funcionales separadas.

URL pública estable:

```text
https://d3lxpalnzir74p.cloudfront.net
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
- **RDS PostgreSQL** persiste feedback y resultados operativos fuera del ciclo de vida de los contenedores.
- **GitHub Actions** despliega automáticamente cada merge en `develop` mediante OIDC y AWS Systems Manager.

El archivo `apprunner.yaml` procede de una evaluación anterior y no forma parte del despliegue activo. La arquitectura vigente es CloudFront + EC2 + RDS.

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
4. Espera a que `GET /api/health` responda correctamente.
5. Comprueba `GET /api/model/info`.
6. Muestra el estado de los servicios y limpia imágenes no utilizadas.

## 5. Despliegue automático

El workflow `.github/workflows/deploy-aws-ec2.yml` se ejecuta tras cada `push` a `develop` y también permite ejecución manual.

Flujo:

1. GitHub solicita credenciales temporales de AWS mediante OIDC.
2. GitHub Actions asume un rol IAM sin almacenar claves de acceso permanentes.
3. AWS Systems Manager envía el comando de despliegue a EC2.
4. EC2 actualiza `develop` con `--ff-only` y ejecuta `scripts/deploy_ec2.sh`.
5. El workflow espera el resultado y falla si el despliegue o el health check no terminan correctamente.

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
GET https://d3lxpalnzir74p.cloudfront.net/api/health
GET https://d3lxpalnzir74p.cloudfront.net/api/model/info
GET https://d3lxpalnzir74p.cloudfront.net/api/feedback/summary
```

Resultado validado el 14 de julio de 2026:

- Frontend accesible desde escritorio y móvil.
- API saludable.
- Champion `random_forest_champion_v0.1.0` cargado.
- Persistencia identificada como `postgresql`.
- Feedback conservado después de reiniciar el backend.
- Despliegue automático desde `develop` completado correctamente.
- Acceso HTTP directo a la IP de EC2 bloqueado después de restringir el origen a CloudFront.

## 8. Diagnóstico

En EC2:

```bash
docker compose --env-file .env.ec2 -f docker-compose.ec2.yml ps
docker compose --env-file .env.ec2 -f docker-compose.ec2.yml logs --tail=100
curl --fail http://localhost/api/health
curl --fail http://localhost/api/model/info
curl --fail http://localhost/api/feedback/summary
```

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
