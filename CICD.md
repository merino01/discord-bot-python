# Configuración de CI/CD

Este documento explica cómo configurar el despliegue automático (CI/CD) del bot de Discord usando GitHub Actions.

## ¿Qué es CI/CD?

CI/CD (Continuous Integration/Continuous Deployment) es una práctica que automatiza el proceso de despliegue. En este caso, cada vez que haces push a la rama `master`, el bot se despliega automáticamente en el servidor.

## Requisitos Previos

1. Un servidor con acceso SSH (Linux recomendado)
2. Docker y Docker Compose instalados en el servidor
3. El repositorio clonado en el servidor
4. Acceso a la configuración de GitHub del repositorio

## Configuración Paso a Paso

### 1. Preparar el Servidor

Primero, asegúrate de que el bot esté funcionando correctamente en tu servidor:

```bash
# En el servidor
cd /ruta/al/proyecto/discord-bot-python
git clone <url-del-repositorio> .
chmod +x deploy.sh
./deploy.sh
```

### 2. Generar Clave SSH (si no existe)

En tu máquina local, genera una clave SSH dedicada para el deployment:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy
```

Esto creará dos archivos:
- `github_deploy` (clave privada)
- `github_deploy.pub` (clave pública)

### 3. Copiar la Clave Pública al Servidor

Copia la clave pública al servidor para permitir el acceso SSH:

```bash
ssh-copy-id -i ~/.ssh/github_deploy.pub usuario@tu-servidor.com
```

O manualmente:

```bash
# Mostrar la clave pública
cat ~/.ssh/github_deploy.pub

# En el servidor, añadirla a authorized_keys
echo "contenido-de-la-clave-publica" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Configurar Secrets en GitHub

Ve a tu repositorio en GitHub y configura los secrets:

1. Navega a **Settings** > **Secrets and variables** > **Actions**
2. Click en **New repository secret**
3. Añade los siguientes secrets:

#### SERVER_HOST
- **Name:** `SERVER_HOST`
- **Value:** IP o hostname de tu servidor (ejemplo: `192.168.1.100` o `miservidor.com`)

#### SERVER_USERNAME
- **Name:** `SERVER_USERNAME`
- **Value:** Usuario SSH del servidor (ejemplo: `ubuntu` o `root`)

#### SSH_PRIVATE_KEY
- **Name:** `SSH_PRIVATE_KEY`
- **Value:** Contenido completo de tu clave privada SSH

Para obtener el contenido de la clave privada:
```bash
cat ~/.ssh/github_deploy
```

Copia **todo** el contenido, incluyendo las líneas `-----BEGIN OPENSSH PRIVATE KEY-----` y `-----END OPENSSH PRIVATE KEY-----`

#### PROJECT_PATH
- **Name:** `PROJECT_PATH`
- **Value:** Ruta completa al proyecto en el servidor (ejemplo: `/home/ubuntu/discord-bot-python`)

#### SERVER_PORT (Opcional)
- **Name:** `SERVER_PORT`
- **Value:** Puerto SSH (por defecto es 22, solo configurar si usas otro puerto)

### 5. Verificar el Workflow

El archivo de workflow está ubicado en `.github/workflows/deploy.yml` y se activa automáticamente cuando:
- Se hace push a la rama `master`

### 6. Probar el Deployment

Para probar que todo funciona correctamente:

1. Haz un pequeño cambio en el código (por ejemplo, añade un comentario)
2. Commit y push a master:
   ```bash
   git add .
   git commit -m "Test CI/CD deployment"
   git push origin master
   ```
3. Ve a la pestaña **Actions** en GitHub para ver el progreso del deployment
4. El workflow se conectará al servidor y ejecutará `deploy.sh`

## Monitoreo del Deployment

### Ver el Estado en GitHub

1. Ve a tu repositorio en GitHub
2. Click en la pestaña **Actions**
3. Verás el historial de todos los deployments
4. Click en cualquier workflow run para ver los detalles y logs

### Ver Logs en el Servidor

Una vez que el deployment termine, puedes ver los logs del bot:

```bash
# En el servidor
cd /ruta/al/proyecto
docker-compose logs -f
```

## Solución de Problemas

### Error: "Permission denied (publickey)"

**Causa:** La clave SSH no está configurada correctamente.

**Solución:**
1. Verifica que copiaste la clave privada completa en `SSH_PRIVATE_KEY`
2. Asegúrate de que la clave pública está en `~/.ssh/authorized_keys` del servidor
3. Verifica los permisos: `chmod 600 ~/.ssh/authorized_keys`

### Error: "Host key verification failed"

**Causa:** GitHub Actions no reconoce el fingerprint del servidor.

**Solución:** El workflow usa `appleboy/ssh-action` que maneja esto automáticamente. Si persiste, puedes añadir `script_stop: true` en el workflow.

### Error: "./deploy.sh: No such file or directory"

**Causa:** La ruta del proyecto (`PROJECT_PATH`) no es correcta.

**Solución:** Verifica que `PROJECT_PATH` apunte al directorio correcto donde está el proyecto.

### El Deployment No Se Activa

**Causa:** El workflow solo se activa en la rama `master`.

**Solución:** 
- Verifica que estás haciendo push a `master` y no a otra rama
- Si quieres activarlo en otras ramas, edita `.github/workflows/deploy.yml`

## Personalización

### Desplegar en Otras Ramas

Para activar el deployment en otras ramas, edita `.github/workflows/deploy.yml`:

```yaml
on:
  push:
    branches:
      - master
      - main
      - production  # Añade las ramas que necesites
```

### Añadir Notificaciones

Puedes añadir notificaciones de Discord al workflow. Ejemplo:

```yaml
- name: Notify Discord
  if: success()
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    title: "Deployment Successful"
    description: "El bot ha sido desplegado exitosamente"
```

### Deployment Manual

Si necesitas ejecutar el deployment manualmente:

```yaml
on:
  push:
    branches:
      - master
  workflow_dispatch:  # Permite ejecución manual
```

## Seguridad

⚠️ **Importante:**

1. **Nunca** compartas tus claves SSH privadas
2. **Nunca** hagas commit de secrets en el código
3. Usa claves SSH dedicadas solo para deployment
4. Revisa regularmente los logs de acceso SSH en tu servidor
5. Considera usar un usuario con permisos limitados para deployment
6. Mantén actualizado el servidor y Docker

## Workflow Completo

El proceso completo de deployment es:

1. Developer hace push a `master`
2. GitHub Actions detecta el push
3. Se ejecuta el workflow `deploy.yml`
4. GitHub Actions se conecta al servidor via SSH
5. Navega al directorio del proyecto
6. Ejecuta `./deploy.sh` que:
   - Hace `git pull` para obtener los cambios
   - Reconstruye la imagen Docker
   - Reinicia el contenedor
   - Muestra el estado y logs
7. El bot se actualiza automáticamente

## Recursos Adicionales

- [Documentación de GitHub Actions](https://docs.github.com/en/actions)
- [SSH Action Documentation](https://github.com/appleboy/ssh-action)
- [Docker Deployment Best Practices](https://docs.docker.com/engine/swarm/stack-deploy/)
