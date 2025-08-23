"""Vista para seleccionar mensajes echo a editar"""

from typing import List
from discord import Interaction, SelectOption
from discord.ui import View, Select
from modules.core import logger
from ..models import EchoMessage
from ..service import EchoService


class EchoMessageSelect(Select):
    """Selector para elegir un mensaje echo a editar"""
    
    def __init__(self, echo_messages: List[EchoMessage], new_content: str, new_is_embed: bool, guild):
        self.echo_messages = echo_messages
        self.new_content = new_content
        self.new_is_embed = new_is_embed
        self.service = EchoService()
        self.guild = guild
        
        # Crear opciones para el selector
        options = []
        for i, message in enumerate(echo_messages):
            # Formatear la fecha
            date_str = message.created_at.strftime("%d/%m %H:%M")
            
            # Obtener el nombre del canal
            channel = guild.get_channel(message.channel_id)
            channel_name = channel.name if channel else f"canal-{message.channel_id}"
            
            # Obtener el nombre del usuario
            user = guild.get_member(message.user_id)
            user_name = user.display_name if user else f"user-{message.user_id}"
            
            # Crear preview del contenido
            if message.is_embed:
                try:
                    import json
                    embed_data = json.loads(message.content)
                    title = embed_data.get('title', '')
                    description = embed_data.get('description', '')
                    content_preview = title or description or 'Embed sin título'
                except (json.JSONDecodeError, KeyError, TypeError):
                    content_preview = 'Embed personalizado'
            else:
                content_preview = message.content
            
            # Truncar contenido
            if len(content_preview) > 30:
                content_preview = content_preview[:27] + "..."
            
            # Crear etiqueta descriptiva
            label = f"{date_str} | #{channel_name} | {content_preview}"
            if len(label) > 100:
                label = label[:97] + "..."
            
            options.append(SelectOption(
                label=label,
                description=f"Por {user_name} - Mensaje {'embed' if message.is_embed else 'texto'}",
                value=message.id,
                emoji="📝" if not message.is_embed else "🎨"
            ))
        
        super().__init__(
            placeholder="Selecciona un mensaje para editar...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: Interaction):
        """Callback cuando se selecciona un mensaje"""
        try:
            # Obtener el mensaje seleccionado
            selected_id = self.values[0]
            selected_message = None
            
            for message in self.echo_messages:
                if message.id == selected_id:
                    selected_message = message
                    break
            
            if not selected_message:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el mensaje seleccionado.",
                    ephemeral=True
                )
                return
            
            # Obtener el canal y el mensaje de Discord
            channel = interaction.guild.get_channel(selected_message.channel_id)
            if not channel:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el canal del mensaje.",
                    ephemeral=True
                )
                return
            
            try:
                discord_message = await channel.fetch_message(selected_message.message_id)
            except Exception:
                await interaction.response.send_message(
                    "❌ No se pudo encontrar el mensaje en Discord. Puede haber sido eliminado.",
                    ephemeral=True
                )
                return
            
            # Editar el mensaje
            try:
                if self.new_is_embed:
                    # Parsear JSON para crear el embed
                    import json
                    from discord import Embed
                    try:
                        embed_data = json.loads(self.new_content)
                        embed = Embed.from_dict(embed_data)
                        await discord_message.edit(content=None, embed=embed)
                    except json.JSONDecodeError:
                        await interaction.response.send_message(
                            "❌ El JSON del embed no es válido.",
                            ephemeral=True
                        )
                        return
                    except Exception as e:
                        await interaction.response.send_message(
                            f"❌ Error al crear el embed: {str(e)}",
                            ephemeral=True
                        )
                        return
                else:
                    # Editar como texto normal
                    await discord_message.edit(content=self.new_content, embed=None)
                
                # Actualizar en la base de datos
                # (Opcional: podrías añadir un método update en el servicio)
                
                await interaction.response.send_message(
                    f"✅ Mensaje editado correctamente en {channel.mention}",
                    ephemeral=True
                )
                
                logger.info(f"Mensaje echo editado por {interaction.user} - ID: {selected_id}")
                
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Error al editar el mensaje: {str(e)}",
                    ephemeral=True
                )
                logger.error(f"Error al editar mensaje echo: {e}")
                
        except Exception as e:
            logger.error(f"Error en callback de EchoMessageSelect: {e}")
            await interaction.response.send_message(
                "❌ Ocurrió un error inesperado.",
                ephemeral=True
            )


class EchoMessageSelectView(View):
    """Vista que contiene el selector de mensajes echo"""
    
    def __init__(self, echo_messages: List[EchoMessage], new_content: str, new_is_embed: bool, guild):
        super().__init__(timeout=300)  # 5 minutos de timeout
        self.add_item(EchoMessageSelect(echo_messages, new_content, new_is_embed, guild))
    
    async def on_timeout(self):
        """Llamado cuando expira el timeout"""
        # Deshabilitar todos los componentes
        for item in self.children:
            item.disabled = True
