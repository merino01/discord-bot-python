"""
i18n.py
Sistema de internacionalización para el bot de Discord.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


class I18n:
    """Clase para manejar las traducciones del bot."""
    
    def __init__(self, language: str = "es-ES", translations_dir: str = "translations"):
        """
        Inicializa el sistema de traducciones.
        
        Args:
            language: Código de idioma (por defecto es-ES)
            translations_dir: Directorio donde se encuentran los archivos de traducción
        """
        self.language = language
        self.translations_dir = Path(translations_dir)
        self.translations: Dict[str, Any] = {}
        self.load_translations()
    
    def load_translations(self) -> None:
        """Carga las traducciones desde el archivo JSON correspondiente al idioma."""
        translation_file = self.translations_dir / f"{self.language}.json"
        
        try:
            with open(translation_file, "r", encoding="utf-8") as file:
                self.translations = json.load(file)
                print(f"Traducciones cargadas desde {translation_file}")
        except FileNotFoundError:
            print(f"⚠️  Archivo de traducción no encontrado: {translation_file}")
            print(f"   Usando idioma por defecto o strings vacíos")
            self.translations = {}
        except json.JSONDecodeError as e:
            print(f"❌ Error al procesar el archivo de traducción: {translation_file}")
            print(f"   Error de JSON: {e}")
            print(f"   Línea {e.lineno}, columna {e.colno}: {e.msg}")
            self.translations = {}
    
    def get(self, key: str, **kwargs) -> str:
        """
        Obtiene una traducción por su clave.
        
        Args:
            key: Clave de la traducción (puede usar notación de punto para objetos anidados)
            **kwargs: Parámetros para formatear el string
            
        Returns:
            String traducido y formateado
        """
        # Navegar por la estructura anidada usando la notación de punto
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    print(f"⚠️  Clave de traducción no encontrada: {key}")
                    return f"[{key}]"
            else:
                print(f"⚠️  Estructura de traducción inválida para la clave: {key}")
                return f"[{key}]"
        
        # Si el valor es un string, formatearlo con los kwargs
        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError as e:
                print(f"⚠️  Parámetro faltante en la traducción '{key}': {e}")
                return value
        
        return str(value)
    
    def t(self, key: str, **kwargs) -> str:
        """
        Alias corto para get().
        
        Args:
            key: Clave de la traducción
            **kwargs: Parámetros para formatear el string
            
        Returns:
            String traducido y formateado
        """
        return self.get(key, **kwargs)


# Instancia global del sistema de traducciones
_i18n_instance: Optional[I18n] = None


def init_i18n(language: str = "es-ES") -> I18n:
    """
    Inicializa el sistema de traducciones global.
    
    Args:
        language: Código de idioma a usar
        
    Returns:
        Instancia de I18n
    """
    global _i18n_instance
    _i18n_instance = I18n(language=language)
    return _i18n_instance


def get_i18n() -> I18n:
    """
    Obtiene la instancia global del sistema de traducciones.
    
    Returns:
        Instancia de I18n
        
    Raises:
        RuntimeError: Si el sistema no ha sido inicializado
    """
    if _i18n_instance is None:
        raise RuntimeError("El sistema de traducciones no ha sido inicializado. Llama a init_i18n() primero.")
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """
    Función de conveniencia para obtener traducciones.
    
    Args:
        key: Clave de la traducción
        **kwargs: Parámetros para formatear el string
        
    Returns:
        String traducido y formateado
    """
    return get_i18n().t(key, **kwargs)


def __(key: str, **kwargs) -> str:
    """
    Función de conveniencia para obtener traducciones (alias corto de t()).
    
    Args:
        key: Clave de la traducción (notación con punto, ej: "clans.messages.createdSuccess")
        **kwargs: Parámetros para formatear el string
        
    Returns:
        String traducido y formateado
    """
    return get_i18n().t(key, **kwargs)
