#!/bin/bash

# Script de despliegue para Discord Bot
# Este script actualiza el código y reinicia el contenedor Docker

set -e

echo "==================================="
echo "🚀 Iniciando despliegue del bot..."
echo "==================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml no encontrado. Asegúrate de estar en el directorio correcto."
    exit 1
fi

# Obtener los últimos cambios del repositorio
echo ""
echo "📥 Obteniendo últimos cambios desde Git..."
git pull

# Reconstruir la imagen de Docker con los cambios
echo ""
echo "🔨 Reconstruyendo imagen Docker..."
docker-compose build

# Reiniciar el contenedor
echo ""
echo "♻️  Reiniciando contenedor..."
docker-compose down
docker-compose up -d

# Mostrar estado del contenedor
echo ""
echo "📊 Estado del contenedor:"
docker-compose ps

# Mostrar los últimos logs
echo ""
echo "📋 Últimos logs:"
docker-compose logs --tail=20

echo ""
echo "==================================="
echo "✅ Despliegue completado con éxito!"
echo "==================================="
echo ""
echo "Para ver los logs en tiempo real, ejecuta:"
echo "  docker-compose logs -f"
