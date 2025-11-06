# Guía de Migración al Sistema i18n

Este documento describe cómo completar la migración del sistema de constantes al sistema i18n.

## Estado Actual

✅ **Completado:**
- Sistema i18n creado en `i18n.py` con función `__()` para acceder a traducciones
- Todas las traducciones extraídas y organizadas en `translations/es-ES.json`
- Configuración de idioma agregada a `settings.py`
- Sistema i18n inicializado en `bot.py`
- Módulo `echo` completamente migrado

⚠️ **Pendiente:**
- Migrar módulos restantes: clans, core, logs_config, channel_formats, triggers, clan_settings, automatic_messages
- Actualizar vistas (views) que tienen texto hardcodeado
- Opcional: Eliminar archivos `constants.py` una vez completada la migración

## Cómo Usar el Sistema i18n

### En archivos Python

1. Importar la función `__`:
```python
from i18n import __
```

2. Reemplazar referencias a constantes:
```python
# Antes:
from . import constants
error_message = constants.ERROR_CLAN_NOT_FOUND

# Después:
from i18n import __
error_message = __("clans.errors.clanNotFound")
```

3. Para mensajes con parámetros:
```python
# Antes:
message = constants.SUCCESS_CLAN_CREATED.format(
    nombre=clan_name,
    text_category=text_cat_id,
    voice_category=voice_cat_id,
    max_members=max_members
)

# Después:
message = __("clans.success.clanCreated",
    nombre=clan_name,
    text_category=text_cat_id,
    voice_category=voice_cat_id,
    max_members=max_members
)
```

### Estructura del archivo de traducción

El archivo `translations/es-ES.json` está organizado por módulos:

```
{
  "clans": {
    "errors": { ... },
    "success": { ... },
    "messages": { ... },
    "embeds": { ... },
    "fields": { ... },
    "commands": { ... },
    "params": { ... }
  },
  "echo": { ... },
  "core": { ... },
  ...
}
```

## Módulos Pendientes de Migración

### 1. modules/clans/
Archivos principales:
- `slash_commands.py` - Comandos principales del sistema de clanes
- `views/*.py` - Vistas con botones e interacciones
- Otros archivos del módulo

### 2. modules/core/
Archivos:
- Utilidades generales que envían mensajes

### 3. modules/logs_config/
Archivos:
- `slash_commands.py` - Comandos de configuración de logs

### 4. modules/channel_formats/
Archivos:
- `slash_commands.py` - Gestión de formatos de canales
- `views.py` - Vistas interactivas

### 5. modules/triggers/
Archivos:
- `slash_commands.py` - Sistema de triggers
- `views.py` - Selección de triggers

### 6. modules/clan_settings/
Archivos:
- `slash_commands.py` - Configuración de clanes

### 7. modules/automatic_messages/
Archivos:
- `slash_commands.py` - Programación de mensajes automáticos
- `views.py` - Constructor de mensajes
- `modal.py` - Modales para configuración

## Proceso de Migración por Módulo

Para cada módulo:

1. **Actualizar imports:**
   ```python
   # Eliminar:
   from . import constants
   
   # Agregar:
   from i18n import __
   ```

2. **Reemplazar referencias a constantes:**
   - Buscar todas las apariciones de `constants.`
   - Reemplazar con la clave correspondiente en `__("")`
   - Verificar que los parámetros de formato coincidan

3. **Actualizar vistas con texto hardcodeado:**
   - Buscar strings literales en español
   - Agregar esos strings a `translations/es-ES.json` si no existen
   - Reemplazar con llamadas a `__()`

4. **Probar:**
   ```bash
   python3 -m py_compile modules/nombre_modulo/*.py
   ```

## Ejemplo Completo

### Antes (usando constants):
```python
from . import constants

@app_commands.command(name="crear", description=constants.COMMAND_CREATE_CLAN_DESC)
@app_commands.describe(
    nombre=constants.PARAM_CLAN_NAME_DESC,
    lider=constants.PARAM_LEADER_DESC
)
async def create_clan(self, interaction, nombre: str, lider: Member):
    if not nombre:
        await interaction.response.send_message(
            constants.ERROR_CLAN_NOT_FOUND,
            ephemeral=True
        )
        return
    
    await interaction.response.send_message(
        constants.SUCCESS_CLAN_CREATED.format(
            nombre=nombre,
            text_category=123,
            voice_category=456,
            max_members=50
        )
    )
```

### Después (usando i18n):
```python
from i18n import __

@app_commands.command(name="crear", description=__("clans.commands.createClan"))
@app_commands.describe(
    nombre=__("clans.params.clanName"),
    lider=__("clans.params.leader")
)
async def create_clan(self, interaction, nombre: str, lider: Member):
    if not nombre:
        await interaction.response.send_message(
            __("clans.errors.clanNotFound"),
            ephemeral=True
        )
        return
    
    await interaction.response.send_message(
        __("clans.success.clanCreated",
            nombre=nombre,
            text_category=123,
            voice_category=456,
            max_members=50
        )
    )
```

## Vistas con Texto Hardcodeado

Algunos ejemplos encontrados en las vistas:

### modules/clans/views/clan_invite_buttons.py
```python
# Línea 58:
content=f"¡Te has unido al clan **{self.clan.name}** exitosamente!"

# Debería ser:
content=__("clans.messages.acceptedInvitation", clan_name=self.clan.name)
```

```python
# Línea 81:
content=f"Has rechazado la invitación al clan **{self.clan.name}**."

# Debería ser:
content=__("clans.messages.rejectedInvitation", clan_name=self.clan.name)
```

```python
# Línea 104:
content=f"La invitación al clan **{self.clan.name}** ha expirado"

# Debería ser:
content=__("clans.messages.invitationExpired", clan_name=self.clan.name)
```

## Archivos constants.py

Una vez completada la migración, los archivos `constants.py` pueden:

1. **Ser eliminados** - Si todos los textos se han migrado
2. **Mantenerse** - Para constantes que NO son textos traducibles (ej: `ONE_SECOND = 1`)

El archivo `constants.py` en la raíz (con ONE_SECOND, ONE_MINUTE, etc.) debe mantenerse ya que contiene constantes numéricas, no textos.

## Verificación

Para verificar que la migración está completa:

1. Buscar referencias a `constants.`:
   ```bash
   grep -r "constants\." modules/ --include="*.py"
   ```

2. Buscar imports de constants:
   ```bash
   grep -r "from .* import constants" modules/ --include="*.py"
   ```

3. Buscar strings hardcodeados en español (más difícil, requiere revisión manual):
   ```bash
   grep -r "\".*❌.*\"" modules/ --include="*.py"
   grep -r "\".*✅.*\"" modules/ --include="*.py"
   ```

## Agregar Nuevos Idiomas

Para agregar un nuevo idioma (ej: en-US):

1. Copiar `translations/es-ES.json` a `translations/en-US.json`
2. Traducir todos los valores (mantener las claves iguales)
3. Actualizar `language` en `config.json` a `"en-US"`
4. Reiniciar el bot

## Notas

- El sistema i18n soporta formato con `{variable}` en los strings
- Las claves usan notación de punto: `"modulo.seccion.clave"`
- Si una clave no se encuentra, se muestra `[clave]` para facilitar debug
- El sistema se inicializa automáticamente al arrancar el bot
