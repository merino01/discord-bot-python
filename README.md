# BOT DE DISCORD

Este es un bot de discord para gestionar el servidor, se pueden configurar **logs**, **triggers**, **mensajes automáticos**, **formatos de canales**, **crear clanes**, etc...

## INSTALACIÓN Y EJECUCIÓN

### Opción 1: Con Docker (Recomendado)

#### Prerrequisitos
- Docker
- Docker Compose

#### Pasos para ejecutar con Docker

1. **Clona el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd discord-bot-python
   ```

2. **Configura el archivo config.json:**
   ```json
   {
       "app_name": "discord-bot",
       "bot_token": "TU_TOKEN_AQUI",
       "guild_id": 1212122343443524324,
       "admin_id": 8767643756437563653,
       "send_to_admin": true
   }
   ```

3. **Ejecuta el bot:**
   
   **En Windows (PowerShell):**
   ```powershell
   .\start.ps1
   ```
   
   **En Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   **O manualmente:**
   ```bash
   # Construir la imagen
   docker build -t discord-bot-python .
   
   # Ejecutar con docker-compose
   docker-compose up -d
   ```

4. **Comandos útiles:**
   ```bash
   # Ver logs en tiempo real
   docker-compose logs -f
   
   # Detener el bot
   docker-compose down
   
   # Ver estado del contenedor
   docker-compose ps
   
   # Reiniciar el bot
   docker-compose restart
   
   # Desplegar actualizaciones (pull + restart)
   ./deploy.sh
   ```

5. **Despliegue de actualizaciones:**
   
   Para actualizar el bot con los últimos cambios del repositorio y reiniciarlo automáticamente:
   
   **En Linux/Mac:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
   
   Este script realiza las siguientes acciones:
   - Descarga los últimos cambios del repositorio (git pull)
   - Reconstruye la imagen Docker con los cambios
   - Reinicia el contenedor
   - Muestra el estado y los logs recientes

6. **CI/CD - Despliegue Automático:**

   El repositorio incluye un workflow de GitHub Actions que despliega automáticamente el bot cuando se realiza un push a la rama `master`.

   **Configuración de secrets en GitHub:**
   
   Para habilitar el despliegue automático, configura los siguientes secrets en tu repositorio de GitHub (Settings > Secrets and variables > Actions):
   
   - `SERVER_HOST`: Dirección IP o hostname del servidor
   - `SERVER_USERNAME`: Usuario SSH del servidor
   - `SSH_PRIVATE_KEY`: Clave privada SSH para autenticación (contenido completo del archivo)
   - `SERVER_PORT`: Puerto SSH del servidor (opcional, por defecto 22)
   - `PROJECT_PATH`: Ruta completa del proyecto en el servidor (ejemplo: `/home/usuario/discord-bot-python`)
   
   **Funcionamiento:**
   
   Cada vez que se hace push a la rama `master`, el workflow automáticamente:
   1. Se conecta al servidor via SSH
   2. Navega al directorio del proyecto
   3. Ejecuta el script `deploy.sh` que actualiza y reinicia el bot
   
   **Ver el estado del deployment:**
   
   Puedes ver el progreso y logs del deployment en la pestaña "Actions" de tu repositorio en GitHub.

### Opción 2: Instalación Local

#### Prerrequisitos
- Python 3.12+
- uv (gestor de paquetes)

#### Pasos para ejecutar localmente

1. **Instala las dependencias:**
   ```bash
   uv sync
   ```

2. **Ejecuta el bot:**
   ```bash
   uv run python main.py
   ```

## CONFIGURACIÓN

Para poder levantar el bot se necesita un archivo `config.json` en la raiz del proyecto.

```json
{
    "app_name": "discord-bot",
    "bot_token": "MTA2Mdfmvksmkvsv78ndsndsn8.4rerevv...",
    "guild_id": 1212122343443524324,
    "admin_id": 8767643756437563653,
    "send_to_admin": true
}
```

### Explicación del archivo de configuración

- **app_name**: El nombre de la aplicación, se usa para ponerlo en los logs
- **bot_token**: El token del bot
- **guild_id**: El ID del servidor donde se va a usar el bot
- **admin_id**: El ID del usuario admin, se le enviarán mensajes si hay algún fallo en el bot
- **send_to_admin**: Valores posibles `true` o `false`. Configura si se quieren enviar mensajes al admin

## LOGS

El bot se encarga de gestionar los siguientes logs

- **chat logs**: Cada vez que se edita o elimina un mensaje
- **voice logs**: Cada vez que un miembro se une, sale o mueve de canal de voz
- **members logs**: Cada vez que un miembros se cambia el apodo, nombre, imagen de perfil, etc...
- **join/leave logs**: Cada vez que un miembro se une o sale del servidor

**Comandos:**

> Para poder usar estos comandos se necesita el permiso: `Administrador`

- **/logs configurar**: Con este comando se pueden configurar los logs, tiene 3 parámetros
  - **tipo_de_log**: El tipo de log que se quiere configurar (chat, voice, members, etc...)
  - **activar**: Si se quiere activar o desactivar el log
  - **canal**: Canal que se quiere usar para enviar los logs
- **/logs listar**: Muestra la configuración de los logs

## TRIGGERS

Se pueden configurar triggers para que el bot responda automáticamente a ciertos mensajes en canales específicos. Los triggers pueden configurarse para detectar palabras o frases en diferentes posiciones del mensaje.

**Comandos:**

> Para usar estos comandos se necesitan los permisos `Gestionar canales` y `Gestionar mensajes`

- **/triggers crear**: Añade un nuevo trigger con los siguientes parámetros:
  - **canal**: Canal donde se verificará el trigger
  - **borrar_mensaje**: Si se debe borrar el mensaje que activa el trigger
  - **respuesta**: Mensaje que enviará el bot cuando se active el trigger
  - **clave**: Palabra o frase que activará el trigger
  - **posicion**: Posición donde debe encontrarse la palabra clave:
    - **Contiene**: La palabra clave puede estar en cualquier parte del mensaje
    - **Empieza por**: El mensaje debe empezar con la palabra clave
    - **Termina por**: El mensaje debe terminar con la palabra clave
    - **Igual a**: El mensaje debe ser exactamente igual a la palabra clave
    - **Texto entre**: Busca texto entre las palabras clave separadas por espacios
    - **Expresión regular**: Usa la palabra clave como expresión regular
  - **tiempo_respuesta**: Tiempo de espera (en segundos) antes de que el bot responda

- **/triggers listar**: Muestra los triggers configurados
  - **id_trigger**: (Opcional) Muestra información de un trigger específico
  - **canal**: (Opcional) Muestra los triggers de un canal específico
  - **persistente**: Si el mensaje debe ser visible para todos los usuarios

- **/triggers eliminar**: Elimina un trigger existente
  - **id_del_trigger**: ID del trigger que se quiere eliminar

**Ejemplo de uso:**

1. Trigger que responde "¡Hola!" cuando alguien dice "hey":

```txt
/triggers crear => canal:#general borrar_mensaje:No respuesta:¡Hola! clave:hey posicion:Contiene
```

## MENSAJES AUTOMÁTICOS

El bot puede enviar mensajes automáticamente en canales específicos. Se pueden configurar para que se envíen:

- En intervalos regulares (cada X segundos/minutos/horas)
- A una hora específica del día

**Comandos:**

> Para usar estos comandos se necesitan los permisos `Gestionar canales` y `Gestionar mensajes`

- **/mensajes_automaticos crear**: Crea un nuevo mensaje automático
  - **canal**: Canal donde se enviará el mensaje
  - **mensaje**: Texto que enviará el bot
  - **intervalo**: (Opcional) Cada cuánto tiempo se enviará el mensaje
  - **tipo_intervalo**: (Opcional) Unidad de tiempo del intervalo:
    - **segundos**
    - **minutos**
    - **horas**
  - **hora**: (Opcional) Hora del día en que se enviará el mensaje (0-23)
  - **minuto**: (Opcional) Minuto en que se enviará el mensaje (0-59)

> **Nota**: Debes especificar o bien un intervalo + tipo_intervalo, o bien una hora + minuto

- **/mensajes_automaticos listar**: Muestra los mensajes automáticos configurados
  - **canal**: (Opcional) Ver solo los mensajes de un canal específico
  - **persistente**: Si el mensaje debe ser visible para todos los usuarios

- **/mensajes_automaticos eliminar**: Elimina un mensaje automático
  - **id_mensaje**: ID del mensaje que se quiere eliminar

**Ejemplos de uso:**

1. Mensaje cada 5 minutos:

```txt
/mensajes_automaticos crear => canal:#anuncios mensaje:"¡No olvides seguir las reglas!" intervalo:5 tipo_intervalo:minutos
```

2. Mensaje diario a una hora específica:

```txt
/mensajes_automaticos crear => canal:#general mensaje:"¡Buenos días a todos!" hora:9 minuto:0
```

3. Recordatorio cada hora:

```txt
/mensajes_automaticos crear => canal:#eventos mensaje:"¡Próximo evento en 3 días!" intervalo:1 tipo_intervalo:hours
```

## FORMATOS DE CANALES

Se pueden configurar formatos específicos para los mensajes en canales usando expresiones regulares. Si un mensaje no cumple con el formato configurado, será eliminado automáticamente.

**Comandos:**

> Para usar estos comandos se necesitan los permisos `Gestionar canales` y `Gestionar mensajes`

- **/formato_canales crear**: Configura un nuevo formato para un canal
  - **canal**: Canal donde se aplicará el formato
  - **formato**: Expresión regular que deben cumplir los mensajes

- **/formato_canales listar**: Muestra los formatos configurados
  - **id_formato**: (Opcional) Ver un formato específico
  - **canal**: (Opcional) Ver formatos de un canal específico
  - **persistente**: Si el mensaje debe ser visible para todos los usuarios

- **/formato_canales eliminar**: Elimina un formato de canal
  - **id_formato**: ID del formato que se quiere eliminar

**Ejemplos de uso:**

1. Canal donde los mensajes deben empezar con "+":

```txt
/formato_canales crear => canal:#comandos formato:"^\+"
```

2. Canal donde solo se permiten números:

```txt
/formato_canales crear => canal:#numeros formato:"^[0-9]+$"
```

3. Canal donde los mensajes deben tener formato de título (3-50 caracteres):

```txt
/formato_canales crear => canal:#anuncios formato:"^[A-Za-zÀ-ÿ0-9\s]{3,50}$"
```

**Expresiones regulares comunes:**

- `^` : Inicio del mensaje
- `$` : Final del mensaje
- `+` : Una o más ocurrencias
- `*` : Cero o más ocurrencias
- `\s` : Espacios en blanco
- `[0-9]` : Números
- `[A-Za-z]` : Letras
- `[A-Za-zÀ-ÿ]` : Letras incluyendo acentos
- `{min,max}` : Rango de repeticiones

## CLANES

Sistema para gestionar clanes dentro del servidor. Cada clan tiene:

- Un rol específico
- Canales privados (texto y voz)
- Líderes y miembros
- Sistema de permisos jerárquico

### Comandos para Miembros

- **/clan unirse**: Unirse a un clan existente
  - **nombre**: Nombre del clan al que quieres unirte

### Comandos para Líderes

> Requiere el rol "Líder de Clan"

- **/clan lider expulsar**: Expulsar a un miembro del clan
  - **miembro**: Usuario a expulsar del clan

### Comandos para el Staff

> Requiere permisos de `Gestionar roles` y `Gestionar canales`

- **/clan mod crear**: Crear un nuevo clan
  - **nombre**: Nombre del clan
  - **lider**: Usuario que será el líder del clan

- **/clan mod info**: Ver información detallada de los clanes
  - **id_clan**: (Opcional) ID del clan específico a consultar
  - Si no se especifica ID, muestra todos los clanes

- **/clan mod eliminar**: Eliminar un clan y todos sus elementos
  - **id_clan**: ID del clan a eliminar

**Ejemplo de uso:**

1. Crear un nuevo clan:

```txt
/clan mod crear => nombre:"Los Invencibles" lider:@Usuario
```

2. Ver información de todos los clanes:

```txt
/clan mod info
```

3. Eliminar un clan específico:

```txt
/clan mod eliminar => id_clan:123e4567-e89b-12d3-a456-426614174000
```

### Características de los Clanes

- **Rol automático**: Se crea un rol específico para el clan
- **Canales privados**:
  - Canal de texto privado para el clan
  - Canal de voz privado para el clan
- **Sistema de permisos**:
  - Los canales son visibles solo para miembros del clan
  - Los líderes pueden gestionar su clan
  - El staff puede gestionar todos los clanes
- **Jerarquía**:
  - Miembros: Acceso básico al clan
  - Líderes: Gestión de miembros
  - Staff: Control total sobre clanes

### Notas Importantes

- Un usuario solo puede estar en un clan a la vez
- Al eliminar un clan:
  - Se elimina el rol asociado
  - Se eliminan los canales del clan
  - Se eliminan todos los registros de la base de datos
- Los canales y roles se crean con permisos específicos para mantener la privacidad

## REQUISITOS

### Requisitos del Sistema

- Python >= 3.12
- Sistema operativo: Windows/Linux/MacOS

### Dependencias Principales

- discord.py >= 2.5.2: Framework para la API de Discord
- pylint >= 3.3.6: Herramienta de análisis de código

### Permisos de Discord Necesarios

El bot necesita los siguientes permisos en el servidor:

- Ver canales
- Gestionar mensajes
- Leer el historial de mensajes
- Enviar mensajes
- Gestionar webhooks (para logs)
- Ver registro de auditoría (para logs)

## INSTALACIÓN

1. Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/discord-bot-python.git
cd discord-bot-python
```

2. Instala las dependencias usando uv:

```bash
# Instalar uv si no está instalado
pip install uv

# Crear entorno virtual e instalar dependencias
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

3. Crea un archivo `config.json` en la raíz del proyecto:

```json
{
    "app_name": "discord-bot",
    "bot_token": "TU_TOKEN_AQUI",
    "guild_id": ID_DEL_SERVIDOR,
    "admin_id": TU_ID_DE_USUARIO,
    "send_to_admin": true
}
```

4. Inicia el bot:

```bash
python main.py
```

## 🌍 SISTEMA DE TRADUCCIONES (i18n)

El bot incluye un sistema completo de internacionalización que permite usar el bot en múltiples idiomas.

### Configurar Idioma

Agrega la clave `language` en tu `config.json`:

```json
{
    "app_name": "discord-bot",
    "bot_token": "TU_TOKEN_AQUI",
    "guild_id": 1212122343443524324,
    "admin_id": 8767643756437563653,
    "send_to_admin": true,
    "language": "es-ES"
}
```

### Idiomas Disponibles

- `es-ES` - Español (España) ✅ Completo

### Agregar Nuevo Idioma

1. Copia el archivo de traducción:
   ```bash
   cp translations/es-ES.json translations/en-US.json
   ```

2. Traduce los valores en el nuevo archivo (mantén las claves iguales)

3. Actualiza tu `config.json`:
   ```json
   {
       "language": "en-US"
   }
   ```

4. Reinicia el bot

### Documentación

- `translations/README.md` - Documentación del sistema de traducciones
- `MIGRATION_GUIDE.md` - Guía para desarrolladores
- `I18N_IMPLEMENTATION_SUMMARY.md` - Resumen de implementación

Para más información sobre el sistema i18n, consulta la documentación en el repositorio.
