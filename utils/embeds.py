"""
    Utility functions for creating embeds.
"""

from datetime import datetime
from discord import Embed, Color, Message, TextChannel, Member

def create_separator(embed: Embed) -> None:
    """
    Create a separator in the embed.
    """
    embed.add_field(name="\u200b", value="\u200b", inline=False)

def get_message_edit_embed(before: Message, after: Message) -> Embed | None:
    """
    Create an embed for the message edit event.
    """
    if not isinstance(after.channel, TextChannel):
        return None

    embed = Embed(
        title="Mensaje editado",
        color=Color.blue(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="Mención del autor",
        value=after.author.mention,
        inline=True
    )
    embed.add_field(
        name="Nombre del autor",
        value=after.author.name,
        inline=True
    )
    embed.add_field(
        name="ID del autor",
        value=after.author.id,
        inline=True
    )

    create_separator(embed)

    embed.add_field(
        name="Mención del canal",
        value=after.channel.mention,
        inline=True
    )
    embed.add_field(
        name="Nombre del canal",
        value=after.channel.name,
        inline=True
    )
    embed.add_field(
        name="ID del canal",
        value=after.channel.id,
        inline=True
    )

    create_separator(embed)

    embed.add_field(
        name="ID del mensaje",
        value=after.id,
        inline=True
    )
    embed.add_field(
        name="Contenido antiguo",
        value=before.content,
        inline=True
    )
    embed.add_field(
        name="Contenido nuevo",
        value=after.content,
        inline=True
    )

    return embed


def get_message_delete_embed(message: Message) -> Embed | None:
    """
    Create an embed for the message delete event.
    """
    if not isinstance(message.channel, TextChannel):
        return None

    embed = Embed(
		title="Mensaje eliminado",
		color=Color.red(),
		timestamp=datetime.now()
	)

    embed.add_field(
		name="Mención del autor",
		value=message.author.mention,
		inline=True
    )
    embed.add_field(
		name="Nombre del autor",
		value=message.author.name,
		inline=True
    )
    embed.add_field(
		name="ID del autor",
		value=message.author.id,
		inline=True
    )

    create_separator(embed)

    embed.add_field(
		name="Mención del canal",
		value=message.channel.mention,
		inline=True
    )
    embed.add_field(
		name="Nombre del canal",
		value=message.channel.name,
		inline=True
    )
    embed.add_field(
		name="ID del canal",
		value=message.channel.id,
		inline=True
    )

    create_separator(embed)

    embed.add_field(
		name="ID del mensaje",
		value=message.id,
		inline=True
    )
    embed.add_field(
		name="Contenido del mensaje",
		value=message.content,
		inline=True
    )

    return embed

def get_member_join_embed(member: Member) -> Embed:
    """
    Create an embed for the member join event.
    """
    embed = Embed(
		title="Un miembro se ha unido al servidor",
		color=Color.dark_green(),
		timestamp=datetime.now()
	)

    embed.add_field(
		name="Mención",
		value=member.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre",
		value=member.name,
		inline=True
	)
    embed.add_field(
		name="ID",
		value=member.id,
		inline=True
	)
    embed.add_field(
		name="Miembros totales en el servidor",
		value=f"{member.guild.member_count} miembros",
		inline=False
	)

    return embed

def get_member_remove_embed(member) -> Embed:
    """
    Create an embed for the member remove event.
    """
    embed = Embed(
		title="Un miembro ha abandonado el servidor",
		color=Color.dark_red(),
		timestamp=datetime.now()
	)

    embed.add_field(
		name="Mención",
		value=member.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre",
		value=member.name,
		inline=True
	)
    embed.add_field(
		name="ID",
		value=member.id,
		inline=True
	)
    embed.add_field(
		name="Miembros totales en el servidor",
		value=f"{member.guild.member_count} miembros",
		inline=False
	)

    return embed


def get_voice_state_join_embed(member, after) -> Embed:
    """
    Crea un embed para el mensaje de estado de voz.
    """
    embed = Embed(
		title="Usuario unido a canal de voz",
		color=Color.green(),
		timestamp=datetime.now()
    )
    embed.add_field(
		name="Mención del usuario",
		value=member.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre del usuario",
		value=member.name,
		inline=True
	)
    embed.add_field(
		name="ID del usuario",
		value=member.id,
		inline=True
	)

    create_separator(embed)

    embed.add_field(
		name="Mención del canal de voz",
		value=after.channel.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre del canal de voz",
		value=after.channel.name,
		inline=True
	)
    embed.add_field(
		name="ID del canal de voz",
		value=after.channel.id,
		inline=True
	)

    return embed


def get_voice_state_leave_embed(member, before) -> Embed:
    """
    Crea un embed para el mensaje de estado de voz.
    """
    embed = Embed(
		title="Usuario salido de canal de voz",
		color=Color.red(),
		timestamp=datetime.now()
	)
    embed.add_field(
		name="Mención del usuario",
		value=member.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre del usuario",
		value=member.name,
		inline=True
	)
    embed.add_field(
		name="ID del usuario",
		value=member.id,
		inline=True
	)

    create_separator(embed)

    embed.add_field(
		name="Mención del canal de voz",
		value=before.channel.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre del canal de voz",
		value=before.channel.name,
		inline=True
	)
    embed.add_field(
		name="ID del canal de voz",
		value=before.channel.id,
		inline=True
	)

    return embed


def get_voice_state_move_embed(member, before, after) -> Embed:
    """
    Crea un embed para el mensaje de estado de voz.
    """
    embed = Embed(
		title="Usuario movido de canal de voz",
		color=Color.blue(),
		timestamp=datetime.now()
	)
    embed.add_field(
		name="Mención del usuario",
		value=member.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre del usuario",
		value=member.name,
		inline=True
	)
    embed.add_field(
		name="ID del usuario",
		value=member.id,
		inline=True
	)

    create_separator(embed)

    embed.add_field(
		name="Mención del canal de voz antiguo",
		value=before.channel.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre del canal de voz antiguo",
		value=before.channel.name,
		inline=True
	)
    embed.add_field(
		name="ID del canal de voz antiguo",
		value=before.channel.id,
		inline=True
	)

    create_separator(embed)

    embed.add_field(
		name="Mención del canal de voz nuevo",
		value=after.channel.mention,
		inline=True
	)
    embed.add_field(
		name="Nombre del canal de voz nuevo",
		value=after.channel.name,
		inline=True
	)
    embed.add_field(
		name="ID del canal de voz nuevo",
		value=after.channel.id,
		inline=True
	)

    return embed

def get_member_update_nick_embed(before: Member, after: Member) -> Embed:
    """
    Create an embed for the member nickname update event.
    """
    embed = Embed(
        title="Cambio de apodo",
        color=Color.blue(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="Mención del usuario",
        value=after.mention,
        inline=True
    )
    embed.add_field(
        name="Nombre del usuario",
        value=after.name,
        inline=True
    )
    embed.add_field(
        name="ID del usuario",
        value=after.id,
        inline=True
    )

    create_separator(embed)

    embed.add_field(
        name="Apodo antiguo",
        value=before.nick,
        inline=True
    )
    embed.add_field(
        name="Apodo nuevo",
        value=after.nick,
        inline=True
    )

    return embed

def get_member_update_username_embed(before: Member, after: Member) -> Embed:
    """
    Create an embed for the member username update event.
    """
    embed = Embed(
        title="Cambio de nombre",
        color=Color.blue(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="Mención del usuario",
        value=after.mention,
        inline=True
    )
    embed.add_field(
        name="ID del usuario",
        value=after.id,
        inline=True
    )

    create_separator(embed)

    embed.add_field(
        name="Nombre antiguo",
        value=before.name,
        inline=True
    )
    embed.add_field(
        name="Nombre nuevo",
        value=after.name,
        inline=True
    )

    return embed

def get_member_update_avatar_embed(before: Member, after: Member) -> Embed:
    """
    Create an embed for the member avatar update event.
    """
    embed = Embed(
        title="Cambio de avatar",
        color=Color.blue(),
        timestamp=datetime.now()
    )
    if after.avatar is not None:
        embed.set_image(
            url=after.avatar.url
        )

    embed.add_field(
        name="Mención del usuario",
        value=after.mention,
        inline=True
    )
    embed.add_field(
        name="Nombre del usuario",
        value=after.name,
        inline=True
    )
    embed.add_field(
        name="ID del usuario",
        value=after.id,
        inline=True
    )

    create_separator(embed)

    embed.add_field(
        name="URL del avatar antiguo",
        value=before.avatar.url if before.avatar else "No hay avatar antiguo",
        inline=True
    )
    embed.add_field(
        name="URL del avatar nuevo",
        value=after.avatar.url if after.avatar else "No hay avatar nuevo",
        inline=True
    )

    return embed

def get_member_update_banner_embed(before: Member, after: Member) -> Embed:
    """
    Create an embed for the member banner update event.
    """
    embed = Embed(
        title="Cambio de banner",
        color=Color.blue(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="Mención del usuario",
        value=after.mention,
        inline=True
    )
    embed.add_field(
        name="Nombre del usuario",
        value=after.name,
        inline=True
    )
    embed.add_field(
        name="ID del usuario",
        value=after.id,
        inline=True
    )

    create_separator(embed)

    embed.add_field(
        name="Banner antiguo",
        value=before.banner.url if before.banner else "No hay banner antiguo",
        inline=True
    )
    embed.add_field(
        name="Banner nuevo",
        value=after.banner.url if after.banner else "No hay banner nuevo",
        inline=True
    )

    return embed

def get_member_update_roles_embed(before: Member, after: Member) -> Embed:
    """
    Create an embed for the member roles update event.
    """
    embed = Embed(
        timestamp=datetime.now()
    )

    embed.add_field(
        name="Mención del usuario",
        value=after.mention,
        inline=True
    )
    embed.add_field(
        name="Nombre del usuario",
        value=after.name,
        inline=True
    )
    embed.add_field(
        name="ID del usuario",
        value=after.id,
        inline=True
    )

    create_separator(embed)

    added_roles = [role for role in after.roles if role not in before.roles]
    removed_roles = [role for role in before.roles if role not in after.roles]

    if added_roles:
        embed.title = "Roles añadidos"
        embed.color = Color.green()
        embed.add_field(
            name="Roles añadidos",
            value=", ".join([role.name for role in added_roles]),
            inline=True
        )

    if removed_roles:
        embed.title = "Roles eliminados"
        embed.color = Color.red()
        embed.add_field(
            name="Roles eliminados",
            value=", ".join([role.name for role in removed_roles]),
            inline=True
        )

    return embed
