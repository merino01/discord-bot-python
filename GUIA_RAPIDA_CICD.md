# Guía Rápida - CI/CD

## ¿Qué se ha añadido?

Se ha configurado un sistema de despliegue automático (CI/CD) que despliega el bot automáticamente cada vez que haces push a la rama `master`.

## Archivos añadidos

1. **`.github/workflows/deploy.yml`** - Workflow de GitHub Actions para deployment automático
2. **`CICD.md`** - Documentación completa de configuración (en español)
3. **`README.md`** - Actualizado con sección de CI/CD

## ¿Cómo funciona?

```
1. Haces git push a master
   ↓
2. GitHub Actions detecta el cambio
   ↓
3. Se conecta a tu servidor por SSH
   ↓
4. Ejecuta deploy.sh en el servidor
   ↓
5. El bot se actualiza automáticamente
```

## Configuración rápida (5 pasos)

### 1. Genera una clave SSH
```bash
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy
```

### 2. Copia la clave al servidor
```bash
ssh-copy-id -i ~/.ssh/github_deploy.pub usuario@tu-servidor.com
```

### 3. Obtén la clave privada
```bash
cat ~/.ssh/github_deploy
```
Copia TODO el contenido (incluyendo BEGIN y END)

### 4. Configura Secrets en GitHub

Ve a: **Tu Repositorio → Settings → Secrets and variables → Actions → New repository secret**

Añade estos 4 secrets:

| Secret | Valor | Ejemplo |
|--------|-------|---------|
| `SERVER_HOST` | IP o hostname del servidor | `192.168.1.100` |
| `SERVER_USERNAME` | Usuario SSH | `ubuntu` |
| `SSH_PRIVATE_KEY` | Clave privada completa | `-----BEGIN OPENSSH...` |
| `PROJECT_PATH` | Ruta del proyecto en servidor | `/home/ubuntu/discord-bot-python` |

### 5. ¡Listo! Prueba haciendo push

```bash
git add .
git commit -m "Test CI/CD"
git push origin master
```

Ve a **Actions** en GitHub para ver el progreso.

## Ver el resultado

- **En GitHub**: Pestaña "Actions" → Click en el workflow run
- **En el servidor**: `docker-compose logs -f`

## Solución de problemas común

### ❌ "Permission denied"
→ Verifica que copiaste la clave privada COMPLETA en `SSH_PRIVATE_KEY`

### ❌ "./deploy.sh: not found"
→ Verifica que `PROJECT_PATH` sea correcto

### ❌ El workflow no se ejecuta
→ Asegúrate de hacer push a `master`, no a otra rama

## Más información

Lee el archivo `CICD.md` para documentación completa y detallada.

## Ventajas

✅ Deployment automático al hacer push
✅ No necesitas SSH manual al servidor
✅ Historial completo de deployments en GitHub
✅ Logs de cada deployment
✅ Fácil de configurar y mantener

## Desactivar CI/CD

Si por alguna razón quieres desactivar el CI/CD temporalmente:

1. Ve a `.github/workflows/deploy.yml`
2. Renombra el archivo a `deploy.yml.disabled`
3. Commit y push

Para reactivarlo, simplemente devuélvele el nombre original.
