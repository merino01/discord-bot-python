"""
Script de ejemplo para usar la API del bot de Discord con Python
Demuestra cómo obtener información de los clanes y realizar operaciones básicas
"""

import requests
import json
from typing import List, Dict, Any

# Configuración
API_URL = "http://localhost:8000"
API_KEY = "tu_clave_api_secreta_aqui"


class DiscordBotAPI:
    """Cliente para la API del bot de Discord"""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {"X-API-Key": api_key}

    def health_check(self) -> Dict[str, Any]:
        """Verificar que la API está activa"""
        response = requests.get(f"{self.api_url}/api/health")
        response.raise_for_status()
        return response.json()

    def get_status(self) -> Dict[str, Any]:
        """Obtener estado de la API (requiere autenticación)"""
        response = requests.get(f"{self.api_url}/api/status", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def list_clans(self) -> List[Dict[str, Any]]:
        """Listar todos los clanes"""
        response = requests.get(f"{self.api_url}/api/clans/", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_clan(self, clan_id: str) -> Dict[str, Any]:
        """Obtener información de un clan específico"""
        response = requests.get(f"{self.api_url}/api/clans/{clan_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_clan_members(self, clan_id: str) -> List[Dict[str, Any]]:
        """Obtener miembros de un clan"""
        response = requests.get(f"{self.api_url}/api/clans/{clan_id}/members", headers=self.headers)
        response.raise_for_status()
        return response.json()


def main():
    """Función principal de ejemplo"""
    print("=== API del Bot de Discord - Script de ejemplo en Python ===\n")

    # Crear cliente de API
    api = DiscordBotAPI(API_URL, API_KEY)

    try:
        # 1. Verificar que la API está activa
        print("1. Verificando que la API está activa...")
        health = api.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Mensaje: {health['message']}\n")

        # 2. Obtener estado autenticado
        print("2. Obteniendo estado de la API (autenticado)...")
        status = api.get_status()
        print(f"   Status: {status['status']}")
        print(f"   Timestamp: {status['timestamp']}\n")

        # 3. Listar todos los clanes
        print("3. Obteniendo lista de todos los clanes...")
        clans = api.list_clans()
        print(f"   Total de clanes: {len(clans)}")

        if clans:
            print("\n   Clanes encontrados:")
            for clan in clans:
                print(f"   - {clan['name']} (ID: {clan['id']})")
                print(f"     Miembros: {clan['member_count']}/{clan['max_members']}")
                print(
                    f"     Canales de texto: {len([c for c in clan['channels'] if c['type'] == 'text'])}"
                )
                print(
                    f"     Canales de voz: {len([c for c in clan['channels'] if c['type'] == 'voice'])}"
                )

            # 4. Obtener detalles del primer clan
            first_clan = clans[0]
            clan_id = first_clan['id']
            print(f"\n4. Obteniendo información detallada del clan: {first_clan['name']}")
            clan_details = api.get_clan(clan_id)
            print(f"   Nombre: {clan_details['name']}")
            print(f"   Role ID: {clan_details['role_id']}")
            print(f"   Creado: {clan_details['created_at']}")

            # 5. Obtener miembros del clan
            print(f"\n5. Obteniendo miembros del clan: {first_clan['name']}")
            members = api.get_clan_members(clan_id)
            print(f"   Total de miembros: {len(members)}")

            if members:
                print("\n   Miembros del clan:")
                for member in members:
                    role_name = "Líder" if member['role'] == 1 else "Miembro"
                    print(f"   - User ID: {member['user_id']} ({role_name})")
                    print(f"     Se unió: {member['joined_at']}")
        else:
            print("   No hay clanes en la base de datos")

        print("\n=== Script finalizado con éxito ===")

    except requests.exceptions.RequestException as e:
        print(f"\nError al conectar con la API: {e}")
        print("Asegúrate de que:")
        print("1. El bot está corriendo con api_enabled=true")
        print("2. El API_KEY es correcto")
        print("3. El API_URL es correcto")
    except Exception as e:
        print(f"\nError inesperado: {e}")


if __name__ == "__main__":
    main()
