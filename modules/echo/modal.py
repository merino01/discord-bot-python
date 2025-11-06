"""Modal para escribir texto en el comando echo"""

from discord import Interaction, TextStyle, Embed
from discord.ui import Modal, TextInput
from modules.core import logger
from .utils import extract_message_info
from . import constants


class EchoTextModal(Modal):
    """Modal para escribir texto de forma más cómoda"""

    def __init__(self, canal, enviar_embed, service):
        super().__init__(title="Escribir mensaje echo")
        self.canal = canal
        self.enviar_embed = enviar_embed
        self.service = service

        # Campo principal para el texto
        self.text_input = TextInput(
            label="Contenido del mensaje" if not enviar_embed else "JSON del embed",
            placeholder=(
                "Escribe aquí tu mensaje..."
                if not enviar_embed
                else '{"title":"Título","description":"Descripción","color":2105893}'
            ),
            style=TextStyle.paragraph,
            required=True,
            max_length=4000,
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: Interaction):
        """Cuando se envía la modal"""
        try:
            texto = self.text_input.value

            # Verificar longitud del mensaje (para texto normal)
            if not self.enviar_embed and len(texto) > 2000:
                return await interaction.response.send_message(
                    constants.ERROR_MESSAGE_TOO_LONG, ephemeral=True
                )

            # Verificar permisos del usuario en el canal de destino
            member_permissions = self.canal.permissions_for(interaction.user)
            if not member_permissions.send_messages:
                return await interaction.response.send_message(
                    constants.ERROR_NO_PERMISSIONS, ephemeral=True
                )

            # Verificar permisos del bot en el canal de destino
            bot_permissions = self.canal.permissions_for(interaction.guild.me)
            if not bot_permissions.send_messages:
                return await interaction.response.send_message(
                    constants.ERROR_NO_PERMISSIONS, ephemeral=True
                )

            try:
                # Enviar el mensaje al canal especificado
                if self.enviar_embed:
                    # Parsear JSON para crear el embed
                    import json
                    from discord import Embed

                    try:
                        embed_data = json.loads(texto)
                    except json.JSONDecodeError:
                        return await interaction.response.send_message(
                            constants.ERROR_INVALID_JSON, ephemeral=True
                        )

                    try:
                        # Crear embed desde JSON
                        embed = Embed.from_dict(embed_data)
                        sent_message = await self.canal.send(embed=embed)

                        # Guardar el mensaje en la base de datos
                        echo_id, _ = self.service.save_echo_message(
                            message_id=sent_message.id,
                            channel_id=self.canal.id,
                            guild_id=interaction.guild.id,
                            user_id=interaction.user.id,
                            content=texto,
                            is_embed=True,
                        )

                        # Confirmar al usuario que el embed fue enviado
                        confirmation_msg = constants.SUCCESS_EMBED_SENT.format(
                            channel=self.canal.mention
                        )
                        if echo_id:
                            confirmation_msg += f"\n{constants.SUCCESS_MESSAGE_SAVED.format(message_id=echo_id[:8])}"

                        await interaction.response.send_message(confirmation_msg, ephemeral=True)

                        logger.info(
                            f"Echo embed modal comando usado por {interaction.user} en #{self.canal.name}"
                        )

                    except Exception as e:
                        return await interaction.response.send_message(
                            constants.ERROR_EMBED_CREATION.format(error=str(e)), ephemeral=True
                        )
                else:
                    # Enviar mensaje normal
                    sent_message = await self.canal.send(texto)

                    # Guardar el mensaje en la base de datos
                    echo_id, _ = self.service.save_echo_message(
                        message_id=sent_message.id,
                        channel_id=self.canal.id,
                        guild_id=interaction.guild.id,
                        user_id=interaction.user.id,
                        content=texto,
                        is_embed=False,
                    )

                    # Confirmar al usuario que el mensaje fue enviado
                    confirmation_msg = constants.SUCCESS_MESSAGE_SENT.format(
                        channel=self.canal.mention
                    )
                    if echo_id:
                        confirmation_msg += (
                            f"\n{constants.SUCCESS_MESSAGE_SAVED.format(message_id=echo_id[:8])}"
                        )

                    await interaction.response.send_message(confirmation_msg, ephemeral=True)

                    logger.info(
                        f"Echo modal comando usado por {interaction.user} en #{self.canal.name}: {texto[:50]}..."
                    )

            except Exception as e:
                logger.error(f"Error en modal echo: {str(e)}")
                await interaction.response.send_message(
                    constants.ERROR_SENDING_MESSAGE.format(error=str(e)), ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error en EchoTextModal.on_submit: {e}")
            await interaction.response.send_message(
                "❌ Ocurrió un error inesperado.", ephemeral=True
            )

    async def on_error(self, interaction: Interaction, error: Exception):
        """Manejo de errores de la modal"""
        logger.error(f"Error en EchoTextModal: {error}")
        await interaction.response.send_message(
            "❌ Ocurrió un error al procesar la modal.", ephemeral=True
        )


class EchoEditModal(Modal):
    """Modal para editar texto de forma más cómoda"""

    def __init__(self, enlace_mensaje, enviar_embed, service, bot_user_id):
        super().__init__(title="Editar mensaje echo")
        self.enlace_mensaje = enlace_mensaje
        self.enviar_embed = enviar_embed
        self.service = service
        self.bot_user_id = bot_user_id

        # Campo principal para el nuevo texto
        self.text_input = TextInput(
            label="Nuevo contenido del mensaje" if not enviar_embed else "Nuevo JSON del embed",
            placeholder=(
                "Escribe aquí el nuevo contenido..."
                if not enviar_embed
                else '{"title":"Nuevo Título","description":"Nueva Descripción","color":2105893}'
            ),
            style=TextStyle.paragraph,
            required=True,
            max_length=4000,
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: Interaction):
        """Cuando se envía la modal de edición"""
        try:
            nuevo_texto = self.text_input.value

            # Verificar longitud del nuevo texto (para texto normal)
            if not self.enviar_embed and len(nuevo_texto) > 2000:
                return await interaction.response.send_message(
                    constants.ERROR_MESSAGE_TOO_LONG, ephemeral=True
                )

            # Si se proporciona un enlace de mensaje
            if self.enlace_mensaje:
                # Parsear el enlace del mensaje
                message_info = extract_message_info(self.enlace_mensaje)
                if not message_info:
                    return await interaction.response.send_message(
                        constants.ERROR_INVALID_MESSAGE_LINK, ephemeral=True
                    )

                channel_id, message_id = message_info

                # Si no hay channel_id, usar el canal actual (caso de solo ID)
                if channel_id is None:
                    target_channel = interaction.channel
                else:
                    target_channel = interaction.guild.get_channel(channel_id)
                    if not target_channel:
                        return await interaction.response.send_message(
                            "❌ No se pudo encontrar el canal del mensaje.", ephemeral=True
                        )

                # Verificar que es un TextChannel
                from discord import TextChannel

                if not isinstance(target_channel, TextChannel):
                    return await interaction.response.send_message(
                        constants.ERROR_INVALID_CHANNEL, ephemeral=True
                    )

                # Intentar obtener el mensaje de Discord
                try:
                    discord_message = await target_channel.fetch_message(message_id)
                except Exception:
                    return await interaction.response.send_message(
                        constants.ERROR_MESSAGE_NOT_IN_DISCORD, ephemeral=True
                    )

                # Verificar permisos: puede editar si es del bot
                if discord_message.author.id != self.bot_user_id:
                    return await interaction.response.send_message(
                        constants.ERROR_MESSAGE_NOT_FROM_BOT, ephemeral=True
                    )

                # Editar el mensaje directamente
                await self._edit_discord_message(interaction, discord_message, nuevo_texto)

            else:
                # Obtener los últimos mensajes echo del servidor
                echo_messages, error = self.service.get_guild_echo_messages(
                    guild_id=interaction.guild.id, limit=10
                )

                if error or not echo_messages:
                    return await interaction.response.send_message(
                        constants.ERROR_NO_ECHO_MESSAGES, ephemeral=True
                    )

                # Para simplificar, editamos el primer mensaje de la lista
                # (En una implementación más completa, podrías mostrar otro selector)
                selected_message = echo_messages[0]

                # Obtener el canal y el mensaje de Discord
                channel = interaction.guild.get_channel(selected_message.channel_id)
                if not channel:
                    return await interaction.response.send_message(
                        "❌ No se pudo encontrar el canal del mensaje.", ephemeral=True
                    )

                try:
                    discord_message = await channel.fetch_message(selected_message.message_id)
                except Exception:
                    return await interaction.response.send_message(
                        constants.ERROR_MESSAGE_NOT_IN_DISCORD, ephemeral=True
                    )

                # Editar el mensaje
                await self._edit_discord_message(interaction, discord_message, nuevo_texto)

        except Exception as e:
            logger.error(f"Error en EchoEditModal.on_submit: {e}")
            await interaction.response.send_message(
                "❌ Ocurrió un error inesperado.", ephemeral=True
            )

    async def _edit_discord_message(self, interaction, discord_message, new_content):
        """Función auxiliar para editar un mensaje de Discord desde la modal"""
        try:
            if self.enviar_embed:
                # Parsear JSON para crear el embed
                import json

                try:
                    embed_data = json.loads(new_content)
                    embed = Embed.from_dict(embed_data)
                    await discord_message.edit(content=None, embed=embed)
                except json.JSONDecodeError:
                    return await interaction.response.send_message(
                        constants.ERROR_INVALID_JSON, ephemeral=True
                    )
                except Exception as e:
                    return await interaction.response.send_message(
                        constants.ERROR_EMBED_CREATION.format(error=str(e)), ephemeral=True
                    )
            else:
                # Editar como texto normal
                await discord_message.edit(content=new_content, embed=None)

            await interaction.response.send_message(
                f"✅ Mensaje editado correctamente en {discord_message.channel.mention}",
                ephemeral=True,
            )

            logger.info(
                f"Mensaje editado por {interaction.user} via modal - Canal: #{discord_message.channel.name} - ID: {discord_message.id}"
            )

        except Exception as e:
            await interaction.response.send_message(
                constants.ERROR_EDITING_MESSAGE.format(error=str(e)), ephemeral=True
            )
            logger.error(f"Error al editar mensaje desde modal: {e}")

    async def on_error(self, interaction: Interaction, error: Exception):
        """Manejo de errores de la modal de edición"""
        logger.error(f"Error en EchoEditModal: {error}")
        await interaction.response.send_message(
            "❌ Ocurrió un error al procesar la modal de edición.", ephemeral=True
        )
