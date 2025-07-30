"""
Procesador de texto para mensajes automáticos
Permite usar variables y formateo especial en los mensajes
"""

import re
from datetime import datetime
from typing import Any
from discord import TextChannel


def process_message_text(text: str, channel: TextChannel, bot: Any) -> str:
    """
    Procesa el texto del mensaje reemplazando variables especiales
    MANTIENE la configuración avanzada (__ADVANCED_CONFIG__) intacta
    
    Variables disponibles:
    - {channel} - Nombre del canal
    - {channel_mention} - Mención del canal
    - {server} - Nombre del servidor
    - {date} - Fecha actual (DD/MM/YYYY)
    - {time} - Hora actual (HH:MM)
    - {datetime} - Fecha y hora completa
    - {member_count} - Cantidad de miembros del servidor
    - {channel_count} - Cantidad de canales del servidor
    """
    
    if not text:
        return text
    
    try:
        # Separar el texto principal de la configuración avanzada
        main_text = text
        advanced_config = ""
        
        if '__ADVANCED_CONFIG__:' in text:
            parts = text.split('__ADVANCED_CONFIG__:', 1)
            main_text = parts[0].strip()
            advanced_config = f"__ADVANCED_CONFIG__:{parts[1]}"
        
        guild = channel.guild
        now = datetime.now()
        
        # Diccionario de variables disponibles
        variables = {
            'channel': channel.name,
            'channel_mention': channel.mention,
            'server': guild.name if guild else 'Servidor Desconocido',
            'date': now.strftime('%d/%m/%Y'),
            'time': now.strftime('%H:%M'),
            'datetime': now.strftime('%d/%m/%Y %H:%M'),
            'member_count': str(guild.member_count) if guild else '0',
            'channel_count': str(len(guild.channels)) if guild else '0',
        }
        
        # Reemplazar variables en el texto PRINCIPAL solamente
        processed_text = main_text
        for var_name, var_value in variables.items():
            pattern = f'{{{var_name}}}'
            processed_text = processed_text.replace(pattern, var_value)
        
        # Procesar menciones especiales
        processed_text = _process_mentions(processed_text, guild)
        
        # Procesar formateo especial
        processed_text = _process_formatting(processed_text)
        
        # Recomponer el texto con la configuración avanzada si existe
        if advanced_config:
            return f"{processed_text}\n{advanced_config}"
        else:
            return processed_text
        
    except Exception:
        # Si hay error en el procesamiento, devolver el texto original
        return text


def _process_mentions(text: str, guild) -> str:
    """Procesa menciones especiales en el texto"""
    if not guild:
        return text
    
    # Patrón para menciones de roles por nombre: @role{nombre_rol}
    role_pattern = r'@role\{([^}]+)\}'
    
    def replace_role_mention(match):
        role_name = match.group(1)
        role = None
        
        # Buscar el rol por nombre (case insensitive)
        for r in guild.roles:
            if r.name.lower() == role_name.lower():
                role = r
                break
        
        return role.mention if role else f"@{role_name}"
    
    text = re.sub(role_pattern, replace_role_mention, text)
    
    # Patrón para menciones de usuarios por nombre: @user{nombre_usuario}
    user_pattern = r'@user\{([^}]+)\}'
    
    def replace_user_mention(match):
        username = match.group(1)
        member = None
        
        # Buscar el miembro por nombre o nickname
        for m in guild.members:
            if (m.name.lower() == username.lower() or 
                (m.nick and m.nick.lower() == username.lower())):
                member = m
                break
        
        return member.mention if member else f"@{username}"
    
    text = re.sub(user_pattern, replace_user_mention, text)
    
    return text


def _process_formatting(text: str) -> str:
    """Procesa formateo especial en el texto"""
    
    # Reemplazar saltos de línea explícitos
    text = text.replace('\\n', '\n')
    
    # Procesar formateo de Discord
    # {bold:texto} -> **texto**
    text = re.sub(r'\{bold:([^}]+)\}', r'**\1**', text)
    
    # {italic:texto} -> *texto*
    text = re.sub(r'\{italic:([^}]+)\}', r'*\1*', text)
    
    # {code:texto} -> `texto`
    text = re.sub(r'\{code:([^}]+)\}', r'`\1`', text)
    
    # {codeblock:texto} -> ```texto```
    text = re.sub(r'\{codeblock:([^}]+)\}', r'```\1```', text)
    
    # {underline:texto} -> __texto__
    text = re.sub(r'\{underline:([^}]+)\}', r'__\1__', text)
    
    # {strikethrough:texto} -> ~~texto~~
    text = re.sub(r'\{strikethrough:([^}]+)\}', r'~~\1~~', text)
    
    # {spoiler:texto} -> ||texto||
    text = re.sub(r'\{spoiler:([^}]+)\}', r'||\1||', text)
    
    return text


def get_available_variables() -> dict:
    """Retorna un diccionario con las variables disponibles y sus descripciones"""
    return {
        '{channel}': 'Nombre del canal actual',
        '{channel_mention}': 'Mención del canal actual (#canal)',
        '{server}': 'Nombre del servidor',
        '{date}': 'Fecha actual (DD/MM/YYYY)',
        '{time}': 'Hora actual (HH:MM)',
        '{datetime}': 'Fecha y hora completa',
        '{member_count}': 'Cantidad de miembros del servidor',
        '{channel_count}': 'Cantidad de canales del servidor',
        '@role{nombre}': 'Mención de rol por nombre',
        '@user{nombre}': 'Mención de usuario por nombre',
        '{bold:texto}': 'Texto en negrita',
        '{italic:texto}': 'Texto en cursiva',
        '{code:texto}': 'Texto en código inline',
        '{codeblock:texto}': 'Bloque de código',
        '{underline:texto}': 'Texto subrayado',
        '{strikethrough:texto}': 'Texto tachado',
        '{spoiler:texto}': 'Texto oculto (spoiler)',
        '\\n': 'Salto de línea'
    }


def preview_processed_text(text: str, channel_name: str = "ejemplo", server_name: str = "Mi Servidor") -> str:
    """
    Genera una vista previa del texto procesado para mostrar al usuario
    """
    now = datetime.now()
    
    preview_variables = {
        'channel': channel_name,
        'channel_mention': f'#{channel_name}',
        'server': server_name,
        'date': now.strftime('%d/%m/%Y'),
        'time': now.strftime('%H:%M'),
        'datetime': now.strftime('%d/%m/%Y %H:%M'),
        'member_count': '150',
        'channel_count': '25',
    }
    
    processed_text = text
    for var_name, var_value in preview_variables.items():
        pattern = f'{{{var_name}}}'
        processed_text = processed_text.replace(pattern, var_value)
    
    # Procesar formateo
    processed_text = _process_formatting(processed_text)
    
    # Simplificar menciones para preview
    processed_text = re.sub(r'@role\{([^}]+)\}', r'@\1', processed_text)
    processed_text = re.sub(r'@user\{([^}]+)\}', r'@\1', processed_text)
    
    return processed_text
