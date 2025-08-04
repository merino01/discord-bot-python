import json
import os
from modules.core import logger
from settings import language as default_language

class Translator:
    def __init__(self, translations_dir="translations", default_locale=default_language):
        self.translations_dir = translations_dir
        self.default_locale = default_locale
        self.translations = self._load_translations()

    def _load_translations(self):
        all_translations = {}
        for filename in os.listdir(self.translations_dir):
            if filename.endswith(".json"):
                locale = os.path.splitext(filename)[0]
                filepath = os.path.join(self.translations_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        all_translations[locale] = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading translation file {filename}: {e}")
        return all_translations

    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """
        Obtiene un texto traducido usando la clave especificada.
        
        Args:
            key: Clave del texto a obtener (ej: 'automaticMessages.errorMessages.errorGettingMessages')
            locale: Idioma específico a usar. Si es None, usa el por defecto.
            **kwargs: Variables para formatear el texto
            
        Returns:
            str: Texto traducido y formateado
        """
        if locale is None:
            locale = self.default_locale
            
        if locale and locale in self.translations:
            text = self._get_nested_value(self.translations[locale], key)
            if text:
                return text.format(**kwargs) if kwargs else text

        # Fallback al idioma por defecto
        if self.default_locale in self.translations:
            text = self._get_nested_value(self.translations[self.default_locale], key)
            if text:
                return text.format(**kwargs) if kwargs else text

        logger.warning(f"Warning: Translation key '{key}' not found for locale '{locale}' or default locale.")
        return key

    def _get_nested_value(self, data, key):
        """Navega por la estructura anidada del JSON usando notación de puntos"""
        keys = key.split('.')
        current_data = data
        for k in keys:
            if isinstance(current_data, dict) and k in current_data:
                current_data = current_data[k]
            else:
                return None
        return current_data


# Instancia global del traductor
_translator_instance = Translator(translations_dir="translations")

def __(key: str, locale: str = None, **kwargs) -> str:
    """
    Función de conveniencia para obtener traducciones.
    
    Args:
        key: Clave del texto (ej: 'automaticMessages.errorMessages.errorGettingMessages')
        locale: Idioma específico (opcional)
        **kwargs: Variables para formatear
        
    Returns:
        str: Texto traducido
    """
    return _translator_instance.get_text(key, locale, **kwargs)