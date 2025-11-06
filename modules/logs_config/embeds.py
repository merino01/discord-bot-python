"""log embeds"""

from datetime import datetime
from discord import Embed, Color, Message, TextChannel, Member
from . import embeds_constants


def create_separator(embed: Embed) -> None:
    embed.add_field(
        name=embeds_constants.SEPARATOR_FIELD, value=embeds_constants.SEPARATOR_FIELD, inline=False
    )


def get_message_edit_embed(before: Message, after: Message) -> Embed | None:
    if not isinstance(after.channel, TextChannel):
        return None

    embed = Embed(
        title=embeds_constants.TITLE_MESSAGE_EDITED, color=Color.blue(), timestamp=datetime.now()
    )

    embed.add_field(
        name=embeds_constants.FIELD_AUTHOR_MENTION, value=after.author.mention, inline=True
    )
    embed.add_field(name=embeds_constants.FIELD_AUTHOR_NAME, value=after.author.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_AUTHOR_ID, value=after.author.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_CHANNEL_MENTION, value=after.channel.mention, inline=True
    )
    embed.add_field(name=embeds_constants.FIELD_CHANNEL_NAME, value=after.channel.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_CHANNEL_ID, value=after.channel.id, inline=True)

    create_separator(embed)

    embed.add_field(name=embeds_constants.FIELD_MESSAGE_ID, value=after.id, inline=True)
    embed.add_field(name=embeds_constants.FIELD_OLD_CONTENT, value=before.content, inline=True)
    embed.add_field(name=embeds_constants.FIELD_NEW_CONTENT, value=after.content, inline=True)

    return embed


def get_message_delete_embed(message: Message) -> Embed | None:
    if not isinstance(message.channel, TextChannel):
        return None

    embed = Embed(
        title=embeds_constants.TITLE_MESSAGE_DELETED, color=Color.red(), timestamp=datetime.now()
    )

    embed.add_field(
        name=embeds_constants.FIELD_AUTHOR_MENTION, value=message.author.mention, inline=True
    )
    embed.add_field(name=embeds_constants.FIELD_AUTHOR_NAME, value=message.author.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_AUTHOR_ID, value=message.author.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_CHANNEL_MENTION, value=message.channel.mention, inline=True
    )
    embed.add_field(
        name=embeds_constants.FIELD_CHANNEL_NAME, value=message.channel.name, inline=True
    )
    embed.add_field(name=embeds_constants.FIELD_CHANNEL_ID, value=message.channel.id, inline=True)

    create_separator(embed)

    embed.add_field(name=embeds_constants.FIELD_MESSAGE_ID, value=message.id, inline=True)
    embed.add_field(name=embeds_constants.FIELD_MESSAGE_CONTENT, value=message.content, inline=True)

    return embed


def get_member_join_embed(member: Member) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_MEMBER_JOINED,
        color=Color.dark_green(),
        timestamp=datetime.now(),
    )

    embed.add_field(name=embeds_constants.FIELD_MENTION, value=member.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_NAME, value=member.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_ID, value=member.id, inline=True)
    embed.add_field(
        name=embeds_constants.FIELD_TOTAL_MEMBERS,
        value=embeds_constants.VALUE_MEMBER_COUNT.format(count=member.guild.member_count),
        inline=False,
    )

    return embed


def get_member_remove_embed(member) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_MEMBER_LEFT,
        color=Color.dark_red(),
        timestamp=datetime.now(),
    )

    embed.add_field(name=embeds_constants.FIELD_MENTION, value=member.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_NAME, value=member.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_ID, value=member.id, inline=True)
    embed.add_field(
        name=embeds_constants.FIELD_TOTAL_MEMBERS,
        value=embeds_constants.VALUE_MEMBER_COUNT.format(count=member.guild.member_count),
        inline=False,
    )

    return embed


def get_voice_state_join_embed(member, after) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_VOICE_JOIN,
        color=Color.green(),
        timestamp=datetime.now(),
    )
    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=member.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_NAME, value=member.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=member.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_VOICE_CHANNEL_MENTION, value=after.channel.mention, inline=True
    )
    embed.add_field(
        name=embeds_constants.FIELD_VOICE_CHANNEL_NAME, value=after.channel.name, inline=True
    )
    embed.add_field(
        name=embeds_constants.FIELD_VOICE_CHANNEL_ID, value=after.channel.id, inline=True
    )

    return embed


def get_voice_state_leave_embed(member, before) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_VOICE_LEAVE,
        color=Color.red(),
        timestamp=datetime.now(),
    )
    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=member.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_NAME, value=member.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=member.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_VOICE_CHANNEL_MENTION, value=before.channel.mention, inline=True
    )
    embed.add_field(
        name=embeds_constants.FIELD_VOICE_CHANNEL_NAME, value=before.channel.name, inline=True
    )
    embed.add_field(
        name=embeds_constants.FIELD_VOICE_CHANNEL_ID, value=before.channel.id, inline=True
    )

    return embed


def get_voice_state_move_embed(member, before, after) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_VOICE_MOVE,
        color=Color.blue(),
        timestamp=datetime.now(),
    )
    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=member.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_NAME, value=member.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=member.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_OLD_VOICE_CHANNEL_MENTION,
        value=before.channel.mention,
        inline=True,
    )
    embed.add_field(
        name=embeds_constants.FIELD_OLD_VOICE_CHANNEL_NAME, value=before.channel.name, inline=True
    )
    embed.add_field(
        name=embeds_constants.FIELD_OLD_VOICE_CHANNEL_ID, value=before.channel.id, inline=True
    )

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_NEW_VOICE_CHANNEL_MENTION,
        value=after.channel.mention,
        inline=True,
    )
    embed.add_field(
        name=embeds_constants.FIELD_NEW_VOICE_CHANNEL_NAME, value=after.channel.name, inline=True
    )
    embed.add_field(
        name=embeds_constants.FIELD_NEW_VOICE_CHANNEL_ID, value=after.channel.id, inline=True
    )

    return embed


def get_member_update_nick_embed(before: Member, after: Member) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_NICK_CHANGE, color=Color.blue(), timestamp=datetime.now()
    )

    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=after.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_NAME, value=after.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(name=embeds_constants.FIELD_OLD_NICK, value=before.nick, inline=True)
    embed.add_field(name=embeds_constants.FIELD_NEW_NICK, value=after.nick, inline=True)

    return embed


def get_member_update_username_embed(before: Member, after: Member) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_USERNAME_CHANGE, color=Color.blue(), timestamp=datetime.now()
    )

    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=after.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(name=embeds_constants.FIELD_OLD_NAME, value=before.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_NEW_NAME, value=after.name, inline=True)

    return embed


def get_member_update_avatar_embed(before: Member, after: Member) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_AVATAR_CHANGE, color=Color.blue(), timestamp=datetime.now()
    )
    if after.avatar is not None:
        embed.set_image(url=after.avatar.url)

    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=after.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_NAME, value=after.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_OLD_AVATAR_URL,
        value=before.avatar.url if before.avatar else embeds_constants.VALUE_NO_OLD_AVATAR,
        inline=True,
    )
    embed.add_field(
        name=embeds_constants.FIELD_NEW_AVATAR_URL,
        value=after.avatar.url if after.avatar else embeds_constants.VALUE_NO_NEW_AVATAR,
        inline=True,
    )

    return embed


def get_member_update_banner_embed(before: Member, after: Member) -> Embed:
    embed = Embed(
        title=embeds_constants.TITLE_BANNER_CHANGE, color=Color.blue(), timestamp=datetime.now()
    )

    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=after.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_NAME, value=after.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=embeds_constants.FIELD_OLD_BANNER,
        value=before.banner.url if before.banner else embeds_constants.VALUE_NO_OLD_BANNER,
        inline=True,
    )
    embed.add_field(
        name=embeds_constants.FIELD_NEW_BANNER,
        value=after.banner.url if after.banner else embeds_constants.VALUE_NO_NEW_BANNER,
        inline=True,
    )

    return embed


def get_member_update_roles_embed(before: Member, after: Member) -> Embed:
    embed = Embed(timestamp=datetime.now())

    embed.add_field(name=embeds_constants.FIELD_USER_MENTION, value=after.mention, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_NAME, value=after.name, inline=True)
    embed.add_field(name=embeds_constants.FIELD_USER_ID, value=after.id, inline=True)

    create_separator(embed)

    added_roles = [role for role in after.roles if role not in before.roles]
    removed_roles = [role for role in before.roles if role not in after.roles]

    if added_roles:
        embed.title = embeds_constants.TITLE_ROLES_ADDED
        embed.color = Color.green()
        embed.add_field(
            name=embeds_constants.FIELD_ROLES_ADDED,
            value=", ".join([role.name for role in added_roles]),
            inline=True,
        )

    if removed_roles:
        embed.title = embeds_constants.TITLE_ROLES_REMOVED
        embed.color = Color.red()
        embed.add_field(
            name=embeds_constants.FIELD_ROLES_REMOVED,
            value=", ".join([role.name for role in removed_roles]),
            inline=True,
        )

    return embed
