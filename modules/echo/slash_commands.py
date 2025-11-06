"""Comandos slash para el módulo Echo"""

import json
from typing import Optional, Union
from discord import app_commands, Interaction, TextChannel, Thread, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from modules.core import logger
from i18n import __
from .service import EchoService
from .views.message_selector import EchoMessageSelectView
from .modal import EchoTextModal, EchoEditModal
from .utils import extract_message_info


class EchoCommands(commands.Cog):
    """Comandos para enviar mensajes (echo) a canales específicos"""

    def __init__(self, bot):
        self.bot = bot
        self.service = EchoService()

    @app_commands.command(name="echo", description=__("echo.commands.echo"))
    @app_commands.describe(
        texto=__("echo.params.text"),
        canal=__("echo.params.channel"),
        enviar_embed=__("echo.params.embed"),
        parrafo=__("echo.params.paragraph")
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def echo(
        self,
        interaction: Interaction,
        texto: str = None,
        canal: Optional[Union[TextChannel, Thread]] = None,
        enviar_embed: bool = False,
        parrafo: bool = False
    ):
        """Envía un mensaje al canal especificado"""

        # Si se especifica párrafo, abrir modal
        if parrafo:
            # Si no se especifica canal, usar el canal actual
            if canal is None:
                canal = interaction.channel

            # Verificar que el canal sea un TextChannel o Thread
            if not isinstance(canal, (TextChannel, Thread)):
                return await interaction.response.send_message(
                    __("echo.errors.invalidChannel"),
                    ephemeral=True
                )

            # Abrir modal para escribir texto
            modal = EchoTextModal(canal, enviar_embed, self.service)
            await interaction.response.send_modal(modal)
            return

        # Si no se usa modal, el texto es obligatorio
        if not texto:
            return await interaction.response.send_message(
                __("echo.errors.textRequired"),
                ephemeral=True
            )

        # Si no se especifica canal, usar el canal actual
        if canal is None:
            canal = interaction.channel

        # Verificar que el canal sea un TextChannel o Thread
        if not isinstance(canal, (TextChannel, Thread)):
            return await interaction.response.send_message(
                __("echo.errors.invalidChannel"),
                ephemeral=True
            )

        # Verificar permisos del usuario en el canal de destino
        member_permissions = canal.permissions_for(interaction.user)
        if not member_permissions.send_messages:
            return await interaction.response.send_message(
                __("echo.errors.noPermissions"),
                ephemeral=True
            )

        # Verificar permisos del bot en el canal de destino
        bot_permissions = canal.permissions_for(interaction.guild.me)
        if not bot_permissions.send_messages:
            return await interaction.response.send_message(
                __("echo.errors.noPermissions"),
                ephemeral=True
            )

        # Verificar longitud del mensaje (para texto normal)
        if not enviar_embed and len(texto) > 2000:
            return await interaction.response.send_message(
                __("echo.errors.messageTooLong"),
                ephemeral=True
            )

        try:
            # Enviar el mensaje al canal especificado
            if enviar_embed:
                # Parsear JSON para crear el embed
                try:
                    embed_data = json.loads(texto)
                except json.JSONDecodeError:
                    return await interaction.response.send_message(
                        __("echo.errors.invalidJson"),
                        ephemeral=True
                    )

                try:
                    # Crear embed desde JSON
                    embed = Embed.from_dict(embed_data)
                    sent_message = await canal.send(embed=embed)

                    # Guardar el mensaje en la base de datos
                    echo_id, _ = self.service.save_echo_message(
                        message_id=sent_message.id,
                        channel_id=canal.id,
                        guild_id=interaction.guild.id,
                        user_id=interaction.user.id,
                        content=texto,
                        is_embed=True
                    )

                    # Confirmar al usuario que el embed fue enviado
                    confirmation_msg = __("echo.success.embedSent", channel=canal.mention)
                    if echo_id:
                        confirmation_msg += f"\n{__('echo.success.messageSaved', message_id=echo_id[:8])}"
                    
                    await interaction.response.send_message(
                        confirmation_msg,
                        ephemeral=True
                    )

                    logger.info(f"Echo embed JSON comando usado por {interaction.user} en #{canal.name}")

                except Exception as e:
                    return await interaction.response.send_message(
                        __("echo.errors.embedCreation", error=str(e)),
                        ephemeral=True
                    )
            else:
                # Enviar mensaje normal
                sent_message = await canal.send(texto)

                # Guardar el mensaje en la base de datos
                echo_id, _ = self.service.save_echo_message(
                    message_id=sent_message.id,
                    channel_id=canal.id,
                    guild_id=interaction.guild.id,
                    user_id=interaction.user.id,
                    content=texto,
                    is_embed=False
                )

                # Confirmar al usuario que el mensaje fue enviado
                confirmation_msg = __("echo.success.messageSent", channel=canal.mention)
                if echo_id:
                    confirmation_msg += f"\n{__('echo.success.messageSaved', message_id=echo_id[:8])}"
                
                await interaction.response.send_message(
                    confirmation_msg,
                    ephemeral=True
                )

                logger.info(f"Echo comando usado por {interaction.user} en #{canal.name}: {texto[:50]}...")

        except Exception as e:
            logger.error(f"Error en comando echo: {str(e)}")
            await interaction.response.send_message(
                __("echo.errors.sendingMessage", error=str(e)),
                ephemeral=True
            )

    @echo.error
    async def echo_error(self, interaction: Interaction, error):
        """Maneja errores del comando echo"""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso 'Gestionar mensajes' para usar este comando.",
                ephemeral=True
            )
        else:
            logger.error(f"Error no manejado en comando echo: {str(error)}")
            await interaction.response.send_message(
                "❌ Ocurrió un error inesperado.",
                ephemeral=True
            )

    @app_commands.command(name="echo_editar", description=__("echo.commands.edit"))
    @app_commands.describe(
        nuevo_texto=__("echo.params.newText"),
        enviar_embed=__("echo.params.newEmbed"),
        enlace_mensaje=__("echo.params.messageId"),
        parrafo=__("echo.params.newParagraph")
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def echo_edit(
        self,
        interaction: Interaction,
        nuevo_texto: str = None,
        enviar_embed: bool = False,
        enlace_mensaje: Optional[str] = None,
        parrafo: bool = False
    ):
        """Edita un mensaje enviado previamente con echo"""
        
        # Si se usa modal para texto largo
        if parrafo and not enlace_mensaje:
            await interaction.response.send_message(__("echo.errors.modalRequiresLink"), ephemeral=True)
            return
        
        if parrafo:
            # Mostrar modal para editar
            modal = EchoEditModal(enlace_mensaje, enviar_embed, self.service, interaction.client.user.id)
            await interaction.response.send_modal(modal)
            return
        
        # Validar que se proporcione texto si no se usa modal
        if not nuevo_texto:
            await interaction.response.send_message(__("echo.errors.textRequired"), ephemeral=True)
            return
        
        # Verificar longitud del nuevo texto (para texto normal)
        if not enviar_embed and len(nuevo_texto) > 2000:
            return await interaction.response.send_message(
                __("echo.errors.messageTooLong"),
                ephemeral=True
            )
        
        # Si se proporciona un enlace de mensaje
        if enlace_mensaje:
            # Parsear el enlace del mensaje
            message_info = extract_message_info(enlace_mensaje)
            if not message_info:
                return await interaction.response.send_message(
                    __("echo.errors.invalidMessageLink"),
                    ephemeral=True
                )
            
            channel_id, message_id = message_info
            
            # Si no hay channel_id, usar el canal actual (caso de solo ID)
            if channel_id is None:
                target_channel = interaction.channel
            else:
                target_channel = interaction.guild.get_channel(channel_id)
                if not target_channel:
                    return await interaction.response.send_message(
                        "❌ No se pudo encontrar el canal del mensaje.",
                        ephemeral=True
                    )
            
            # Verificar que es un TextChannel o Thread
            if not isinstance(target_channel, (TextChannel, Thread)):
                return await interaction.response.send_message(
                    __("echo.errors.invalidChannel"),
                    ephemeral=True
                )
            
            # Intentar obtener el mensaje de Discord
            try:
                discord_message = await target_channel.fetch_message(message_id)
            except Exception:
                return await interaction.response.send_message(
                    __("echo.errors.messageNotInDiscord"),
                    ephemeral=True
                )
            
            # Verificar permisos: puede editar si es del bot
            can_edit = False
            error_reason = None
            
            # Verificar si el mensaje es del bot
            if discord_message.author.id == interaction.client.user.id:
                can_edit = True
            else:
                error_reason = __("echo.errors.messageNotFromBot")
            
            if not can_edit:
                return await interaction.response.send_message(
                    error_reason,
                    ephemeral=True
                )
            
            # Editar el mensaje directamente
            await self._edit_discord_message(interaction, discord_message, nuevo_texto, enviar_embed)
        
        else:
            # Obtener los últimos mensajes echo del servidor (no solo del usuario)
            echo_messages, error = self.service.get_guild_echo_messages(
                guild_id=interaction.guild.id,
                limit=10
            )
            
            if error or not echo_messages:
                return await interaction.response.send_message(
                    __("echo.errors.noEchoMessages"),
                    ephemeral=True
                )
            
            # Mostrar selector de mensajes
            view = EchoMessageSelectView(echo_messages, nuevo_texto, enviar_embed, interaction.guild)
            embed = Embed(
                title=__("echo.embeds.selectMessageTitle"),
                description=__("echo.embeds.selectMessageDescription"),
                color=Color.blue()
            )
            
            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )

    async def _edit_discord_message(self, interaction: Interaction, discord_message, new_content: str, is_embed: bool):
        """Función auxiliar para editar un mensaje de Discord directamente"""
        try:
            # Editar el mensaje
            try:
                if is_embed:
                    # Parsear JSON para crear el embed
                    try:
                        embed_data = json.loads(new_content)
                        embed = Embed.from_dict(embed_data)
                        await discord_message.edit(content=None, embed=embed)
                    except json.JSONDecodeError:
                        return await interaction.response.send_message(
                            __("echo.errors.invalidJson"),
                            ephemeral=True
                        )
                    except Exception as e:
                        return await interaction.response.send_message(
                            __("echo.errors.embedCreation", error=str(e)),
                            ephemeral=True
                        )
                else:
                    # Editar como texto normal
                    await discord_message.edit(content=new_content, embed=None)
                
                await interaction.response.send_message(
                    f"✅ Mensaje editado correctamente en {discord_message.channel.mention}",
                    ephemeral=True
                )
                
                logger.info(f"Mensaje editado por {interaction.user} - Canal: #{discord_message.channel.name} - ID: {discord_message.id}")
                
            except Exception as e:
                await interaction.response.send_message(
                    __("echo.errors.editingMessage", error=str(e)),
                    ephemeral=True
                )
                logger.error(f"Error al editar mensaje: {e}")
                
        except Exception as e:
            logger.error(f"Error en _edit_discord_message: {e}")
            await interaction.response.send_message(
                "❌ Ocurrió un error inesperado.",
                ephemeral=True
            )

    @echo_edit.error
    async def echo_edit_error(self, interaction: Interaction, error):
        """Maneja errores del comando echo_editar"""
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso 'Gestionar mensajes' para usar este comando.",
                ephemeral=True
            )
        else:
            logger.error(f"Error no manejado en comando echo_editar: {str(error)}")
            await interaction.response.send_message(
                "❌ Ocurrió un error inesperado.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(EchoCommands(bot), guild=Object(id=guild_id))
