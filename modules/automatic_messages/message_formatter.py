"""
Módulo para formatear y enviar mensajes automáticos con soporte para embeds e imágenes
"""
import json
import discord
import io
import urllib.request
import urllib.parse
import asyncio
import concurrent.futures
from typing import Optional, Dict, Any

def parse_message_config(text: str) -> Dict[str, Any]:
    """
    Parsea un mensaje que puede contener configuración avanzada
    
    Args:
        text: Texto del mensaje que puede contener __ADVANCED_CONFIG__
        
    Returns:
        Dict con 'text', 'embed_config', 'embed_image_url' y 'attachment_image_url'
    """
    config = {
        'text': text,
        'embed_config': None,
        'embed_image_url': None,
        'attachment_image_url': None
    }
    
    # Buscar configuración avanzada en el texto
    if '__ADVANCED_CONFIG__:' in text:
        parts = text.split('__ADVANCED_CONFIG__:', 1)
        config['text'] = parts[0].strip()
        
        try:
            advanced_config = json.loads(parts[1])
            config['embed_config'] = advanced_config.get('embed')
            config['attachment_image_url'] = advanced_config.get('attachment_image_url')
            
            # Extraer imagen del embed si existe
            if config['embed_config'] and config['embed_config'].get('image'):
                config['embed_image_url'] = config['embed_config']['image']
                
        except json.JSONDecodeError:
            # Si no se puede parsear, ignorar la configuración avanzada
            pass
    
    return config

def create_color_from_string(color_str: str) -> discord.Color:
    """
    Convierte un string de color a discord.Color
    
    Args:
        color_str: String del color ('blue', 'red', 'green', etc. o hex '#FF0000')
        
    Returns:
        discord.Color
    """
    if color_str.startswith('#'):
        try:
            return discord.Color(int(color_str[1:], 16))
        except ValueError:
            return discord.Color.blue()
    
    color_map = {
        'blue': discord.Color.blue(),
        'red': discord.Color.red(),
        'green': discord.Color.green(),
        'yellow': discord.Color.yellow(),
        'orange': discord.Color.orange(),
        'purple': discord.Color.purple(),
        'magenta': discord.Color.magenta(),
        'gold': discord.Color.gold(),
        'dark_blue': discord.Color.dark_blue(),
        'dark_red': discord.Color.dark_red(),
        'dark_green': discord.Color.dark_green(),
        'dark_magenta': discord.Color.dark_magenta(),
        'dark_purple': discord.Color.dark_purple(),
        'dark_gold': discord.Color.dark_gold(),
        'light_grey': discord.Color.light_grey(),
        'dark_grey': discord.Color.dark_grey(),
        'blurple': discord.Color.blurple(),
        'greyple': discord.Color.greyple(),
    }
    
    return color_map.get(color_str.lower(), discord.Color.blue())

def _download_image_sync(url: str) -> Optional[discord.File]:
    """
    Descarga una imagen desde una URL de forma sincrónica
    """
    try:
        # Validar que la URL sea válida
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None
        
        # Descargar la imagen
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                # Leer el contenido de la imagen
                image_data = response.read()
                
                # Obtener la extensión del archivo desde la URL o Content-Type
                content_type = response.headers.get('Content-Type', '').lower()
                filename = 'image.png'  # Default
                
                if 'image/png' in content_type:
                    filename = 'image.png'
                elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
                    filename = 'image.jpg'
                elif 'image/gif' in content_type:
                    filename = 'image.gif'
                elif 'image/webp' in content_type:
                    filename = 'image.webp'
                else:
                    # Intentar obtener extensión de la URL
                    if '.' in url:
                        ext = url.split('.')[-1].split('?')[0].lower()
                        if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                            filename = f'image.{ext}'
                
                # Crear un BytesIO object y el discord.File
                image_buffer = io.BytesIO(image_data)
                return discord.File(image_buffer, filename=filename)
                
    except Exception as e:
        print(f"Error descargando imagen desde {url}: {e}")
        return None

async def download_image(url: str) -> Optional[discord.File]:
    """
    Descarga una imagen desde una URL de forma asíncrona
    
    Args:
        url: URL de la imagen a descargar
        
    Returns:
        discord.File si se descarga correctamente, None si hay error
    """
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _download_image_sync, url)

async def send_formatted_message(channel: discord.TextChannel, text: str) -> Optional[discord.Message]:
    """
    Envía un mensaje formateado que puede incluir embed e imagen
    
    Args:
        channel: Canal donde enviar el mensaje
        text: Texto del mensaje (puede contener configuración avanzada)
        
    Returns:
        El mensaje enviado o None si hubo error
    """
    try:
        config = parse_message_config(text)
        
        # Preparar argumentos base
        kwargs = {}
        
        # Si hay configuración de embed
        if config['embed_config']:
            embed = discord.Embed()
            
            if config['embed_config']['title']:
                embed.title = config['embed_config']['title']
            
            if config['embed_config']['description']:
                embed.description = config['embed_config']['description']
            elif config['text']:  # Solo usar el texto si existe
                embed.description = config['text']
            
            embed.color = create_color_from_string(config['embed_config']['color'])
            
            # Si hay imagen del embed, añadirla al embed
            if config['embed_image_url']:
                embed.set_image(url=config['embed_image_url'])
            
            kwargs['embed'] = embed
            
            # Si hay texto y no está en la descripción del embed, enviarlo también
            if config['text'] and config['text'] != embed.description:
                kwargs['content'] = config['text']
        
        else:
            # Mensaje simple con o sin imagen
            if config['text']:  # Solo añadir contenido si hay texto
                kwargs['content'] = config['text']
        
        # Manejar imagen de attachment (independiente del embed)
        if config['attachment_image_url']:
            image_file = await download_image(config['attachment_image_url'])
            if image_file:
                kwargs['file'] = image_file
            else:
                # Fallback: mostrar la URL si no se pudo descargar
                print(f"No se pudo descargar la imagen, mostrando URL: {config['attachment_image_url']}")
                if 'content' in kwargs:
                    kwargs['content'] += f"\n{config['attachment_image_url']}"
                else:
                    kwargs['content'] = config['attachment_image_url']
        
        # Verificar que hay algo que enviar
        if not any(key in kwargs for key in ['content', 'embed', 'file']):
            print("Error: No hay contenido para enviar (ni texto, ni embed, ni imagen)")
            return None
        
        return await channel.send(**kwargs)
        
    except Exception as e:
        print(f"Error enviando mensaje formateado: {e}")
        # Fallback: enviar solo el texto original si existe
        try:
            clean_text = text.split('__ADVANCED_CONFIG__:')[0].strip()
            if clean_text:  # Solo enviar si hay texto
                return await channel.send(clean_text)
            else:
                print("No hay texto de fallback para enviar")
                return None
        except Exception:
            return None
        if not any(key in kwargs for key in ['content', 'embed', 'file']):
            print("Error: No hay contenido para enviar (ni texto, ni embed, ni imagen)")
            return None
        
        return await channel.send(**kwargs)
        
    except Exception as e:
        print(f"Error enviando mensaje formateado: {e}")
        # Fallback: enviar solo el texto original si existe
        try:
            clean_text = text.split('__ADVANCED_CONFIG__:')[0].strip()
            if clean_text:  # Solo enviar si hay texto
                return await channel.send(clean_text)
            else:
                print("No hay texto de fallback para enviar")
                return None
        except Exception:
            return None

def format_message_preview(text: str) -> Dict[str, str]:
    """
    Crea un preview del mensaje para mostrar en la UI
    
    Args:
        text: Texto del mensaje
        
    Returns:
        Dict con 'text_preview', 'embed_preview', 'image_preview'
    """
    config = parse_message_config(text)
    
    preview = {
        'text_preview': config['text'][:200] + ('...' if len(config['text']) > 200 else '') if config['text'] else '(Sin texto)',
        'embed_preview': '',
        'image_preview': ''
    }
    
    if config['embed_config']:
        title = config['embed_config']['title'] or 'Sin título'
        color = config['embed_config']['color']
        preview['embed_preview'] = f"🎨 **Embed**: {title} ({color})"
    
    if config['embed_image_url']:
        preview['image_preview'] = f"🖼️ **Imagen Embed**: {config['embed_image_url'][:50]}..."
    
    if config['attachment_image_url']:
        if preview['image_preview']:
            preview['image_preview'] += f"\n📎 **Imagen Attachment**: {config['attachment_image_url'][:50]}..."
        else:
            preview['image_preview'] = f"📎 **Imagen Attachment**: {config['attachment_image_url'][:50]}..."
    
    return preview
