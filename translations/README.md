# Sistema de Traducciones / Translation System

Este directorio contiene los archivos de traducción para el bot de Discord.

## Estructura

Cada idioma tiene su propio archivo JSON con el formato: `{código-idioma}.json`

Ejemplo:
- `es-ES.json` - Español (España)
- `en-US.json` - Inglés (Estados Unidos)
- `pt-BR.json` - Portugués (Brasil)

## Formato del Archivo

Los archivos de traducción están organizados por módulos y secciones:

```json
{
  "nombreModulo": {
    "seccion": {
      "clave": "Texto traducido con {parametros}"
    }
  }
}
```

### Ejemplo Real

```json
{
  "clans": {
    "errors": {
      "clanNotFound": "❌ Clan no encontrado."
    },
    "success": {
      "clanCreated": "✅ Clan {nombre} creado con éxito."
    }
  }
}
```

## Uso en el Código

```python
from i18n import __

# Texto simple
mensaje = __("clans.errors.clanNotFound")

# Texto con parámetros
mensaje = __("clans.success.clanCreated", nombre="MiClan")
```

## Agregar un Nuevo Idioma

1. Copiar `es-ES.json` con el nuevo nombre (ej: `en-US.json`)
2. Traducir todos los valores, **manteniendo las claves iguales**
3. Actualizar `language` en `config.json`
4. Reiniciar el bot

## Secciones Organizadas

Cada módulo típicamente contiene:

- **errors**: Mensajes de error
- **success**: Mensajes de éxito
- **messages**: Mensajes informativos
- **embeds**: Títulos y descripciones de embeds
- **fields**: Nombres de campos en embeds
- **values**: Valores predefinidos
- **commands**: Descripciones de comandos
- **params**: Descripciones de parámetros
- **buttons**: Etiquetas de botones

## Parámetros en Textos

Los parámetros se especifican usando `{nombre_parametro}`:

```json
{
  "mensaje": "El usuario {user} ha sido {action} del clan {clan_name}."
}
```

Uso:
```python
__("mensaje", user="@Juan", action="expulsado", clan_name="Warriors")
# Resultado: "El usuario @Juan ha sido expulsado del clan Warriors."
```

## Emojis

Los emojis están incluidos directamente en los textos:

```json
{
  "success": "✅ Operación exitosa",
  "error": "❌ Ha ocurrido un error",
  "info": "ℹ️ Información importante"
}
```

## Validación

Para validar que un archivo JSON es válido:

```bash
python3 -c "import json; json.load(open('translations/es-ES.json'))"
```

Si no hay errores, el archivo es válido.

## Convenciones

1. **Claves en camelCase**: `clanNotFound`, `userJoinedClan`
2. **Valores en español natural**: Incluir emojis, formato, etc.
3. **Parámetros en snake_case**: `{clan_name}`, `{user_id}`
4. **Mantener estructura consistente** entre idiomas

## Módulos Incluidos

- `clans` - Sistema de clanes
- `echo` - Envío de mensajes
- `core` - Utilidades generales
- `logsConfig` - Configuración de logs
- `channelFormats` - Formatos de canales
- `triggers` - Sistema de triggers
- `clanSettings` - Configuración de clanes
- `automaticMessages` - Mensajes automáticos

## Soporte

Para más información, consultar `MIGRATION_GUIDE.md` en la raíz del proyecto.
