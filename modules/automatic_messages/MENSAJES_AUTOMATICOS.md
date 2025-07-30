
# Guía de Usuario: Mensajes Automáticos en Discord

## ¿Qué son los mensajes automáticos?

Los mensajes automáticos te permiten programar mensajes que el bot enviará de forma automática en canales o categorías de tu servidor Discord. Puedes usarlos para recordatorios, anuncios, mensajes de bienvenida, y mucho más.

---

## ¿Qué puedo hacer con los mensajes automáticos?

- **Programar mensajes** para que se envíen en horarios específicos o cuando se crea un canal.
- **Personalizar el contenido** usando variables dinámicas (por ejemplo, el nombre del canal, la fecha, el número de miembros, etc.).
- **Formatear el texto** con negrita, cursiva, código, spoiler, etc.
- **Mencionar roles o usuarios** automáticamente en el mensaje.

---

## ¿Cómo programo un mensaje automático?

1. Usa el comando `/mensajes_automaticos programar` en tu servidor.
2. Elige el tipo de programación:
   - **Intervalo**: Se repite cada cierto tiempo (ej. cada hora).
   - **Diario**: Se envía a una hora específica cada día.
   - **Semanal**: Se envía en días y horas específicas de la semana.
   - **Al crear canal**: Se envía cuando se crea un canal en una categoría.
3. Selecciona el canal o categoría donde quieres que se envíe el mensaje.
4. Escribe el contenido del mensaje y personalízalo usando las variables y el formato que desees.
5. Confirma la programación y ¡listo!

---

## ¿Qué variables puedo usar en mis mensajes?

Puedes incluir las siguientes variables en el texto del mensaje. El bot las reemplazará automáticamente:

- `{channel}`: Nombre del canal
- `{channel_mention}`: Mención al canal (ejemplo: #general)
- `{server}`: Nombre del servidor
- `{date}`: Fecha actual (DD/MM/YYYY)
- `{time}`: Hora actual (HH:MM)
- `{datetime}`: Fecha y hora completa
- `{member_count}`: Número de miembros en el servidor
- `{channel_count}`: Número de canales en el servidor
- `@role{nombre}`: Menciona un rol por su nombre (ejemplo: `@role{Moderador}`)
- `@user{nombre}`: Menciona un usuario por su nombre o apodo (ejemplo: `@user{Juan}`)

---

## ¿Cómo puedo dar formato al texto?

Puedes usar los siguientes formatos especiales en tu mensaje:

- `{bold:Texto}` → **Texto en negrita**
- `{italic:Texto}` → *Texto en cursiva*
- `{code:Texto}` → `Texto en código`
- `{codeblock:Texto}` → Bloque de código
- `{underline:Texto}` → __Texto subrayado__
- `{strikethrough:Texto}` → ~~Texto tachado~~
- `{spoiler:Texto}` → ||Texto oculto||
- `\n` → Salto de línea

**Ejemplo:**  
`¡Hola {channel_mention}! Hoy es {date} y somos {member_count} miembros. {bold:No olvides participar.}`

---

## ¿Cómo veo o elimino mensajes automáticos?

- Usa `/mensajes_automaticos listar` para ver todos los mensajes programados.
- Usa `/mensajes_automaticos eliminar` para borrar mensajes automáticos que ya no necesites.

---

## Preguntas Frecuentes

**¿Puedo mencionar a un rol o usuario aunque cambie el nombre?**  
Sí, el bot buscará el nombre actual del rol o usuario y lo mencionará correctamente.

**¿Puedo usar emojis y enlaces en el mensaje?**  
¡Por supuesto! Escribe el mensaje como lo harías normalmente en Discord.

**¿Puedo editar un mensaje automático después de crearlo?**  
Actualmente, debes eliminar el mensaje y crear uno nuevo con los cambios.

---

## Consejos

- Usa variables para que tus mensajes sean dinámicos y útiles.
- Aprovecha el formato para destacar información importante.
- Programa recordatorios, anuncios, mensajes de bienvenida, y más.

---

¿Tienes dudas o necesitas ayuda? Contacta a los administradores del servidor.
