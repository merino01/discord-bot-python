#!/bin/bash
# Script de ejemplo para usar la API del bot de Discord
# Este script demuestra cómo obtener información de los clanes usando curl

# Configuración
API_URL="http://localhost:8000"
API_KEY="tu_clave_api_secreta_aqui"

# Colores para la salida
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== API del Bot de Discord - Script de ejemplo ===${NC}"
echo ""

# 1. Verificar que la API está activa
echo -e "${GREEN}1. Verificando que la API está activa...${NC}"
curl -s "$API_URL/api/health" | jq '.'
echo ""

# 2. Listar todos los clanes
echo -e "${GREEN}2. Obteniendo lista de todos los clanes...${NC}"
CLANS=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/api/clans/")
echo "$CLANS" | jq '.'
echo ""

# 3. Obtener el primer clan (si existe)
CLAN_COUNT=$(echo "$CLANS" | jq 'length')
if [ "$CLAN_COUNT" -gt 0 ]; then
    CLAN_ID=$(echo "$CLANS" | jq -r '.[0].id')
    CLAN_NAME=$(echo "$CLANS" | jq -r '.[0].name')
    
    echo -e "${GREEN}3. Obteniendo información del clan: $CLAN_NAME${NC}"
    curl -s -H "X-API-Key: $API_KEY" "$API_URL/api/clans/$CLAN_ID" | jq '.'
    echo ""
    
    echo -e "${GREEN}4. Obteniendo miembros del clan: $CLAN_NAME${NC}"
    MEMBERS=$(curl -s -H "X-API-Key: $API_KEY" "$API_URL/api/clans/$CLAN_ID/members")
    echo "$MEMBERS" | jq '.'
    
    MEMBER_COUNT=$(echo "$MEMBERS" | jq 'length')
    echo -e "${BLUE}Total de miembros en el clan: $MEMBER_COUNT${NC}"
else
    echo "No hay clanes en la base de datos"
fi

echo ""
echo -e "${BLUE}=== Script finalizado ===${NC}"
