# BOT DE DISCORD

Este es un bot de discord para gestionar el servidor, se pueden configurar **logs**, **triggers**, **mensajes automáticos**, **formatos de canales**, etc...

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
/formato_canales crear canal:#comandos formato:"^\+"
```

2. Canal donde solo se permiten números:

```txt
/formato_canales crear canal:#numeros formato:"^[0-9]+$"
```

3. Canal donde los mensajes deben tener formato de título (3-50 caracteres):

```txt
/formato_canales crear canal:#anuncios formato:"^[A-Za-zÀ-ÿ0-9\s]{3,50}$"
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
