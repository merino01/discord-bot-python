"""log embeds"""

from datetime import datetime
from discord import Embed, Color, Message, TextChannel, Member
from i18n import __


def create_separator(embed: Embed) -> None:
    embed.add_field(name=__("logsConfig.embedValues.separator"), value=__("logsConfig.embedValues.separator"), inline=False)


def get_message_edit_embed(before: Message, after: Message) -> Embed | None:
    if not isinstance(after.channel, TextChannel):
        return None

    embed = Embed(title=__("logsConfig.embedTitles.messageEdited"), color=Color.blue(), timestamp=datetime.now())

    embed.add_field(name=__("logsConfig.embedFields.authorMention"), value=after.author.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.authorName"), value=after.author.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.authorId"), value=after.author.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.channelMention"), value=after.channel.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.channelName"), value=after.channel.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.channelId"), value=after.channel.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.messageId"), value=after.id, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.oldContent"), value=before.content, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.newContent"), value=after.content, inline=True)

    return embed


def get_message_delete_embed(message: Message) -> Embed | None:
    if not isinstance(message.channel, TextChannel):
        return None

    embed = Embed(title=__("logsConfig.embedTitles.messageDeleted"), color=Color.red(), timestamp=datetime.now())

    embed.add_field(name=__("logsConfig.embedFields.authorMention"), value=message.author.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.authorName"), value=message.author.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.authorId"), value=message.author.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.channelMention"), value=message.channel.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.channelName"), value=message.channel.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.channelId"), value=message.channel.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.messageId"), value=message.id, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.messageContent"), value=message.content, inline=True)

    return embed


def get_member_join_embed(member: Member) -> Embed:
    embed = Embed(
        title=__("logsConfig.embedTitles.memberJoined"),
        color=Color.dark_green(),
        timestamp=datetime.now(),
    )

    embed.add_field(name=__("logsConfig.embedFields.mention"), value=member.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.name"), value=member.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.id"), value=member.id, inline=True)
    embed.add_field(
        name=__("logsConfig.embedFields.totalMembers"),
        value=__("logsConfig.embedValues.memberCount", count=member.guild.member_count),
        inline=False,
    )

    return embed


def get_member_remove_embed(member) -> Embed:
    embed = Embed(
        title=__("logsConfig.embedTitles.memberLeft"),
        color=Color.dark_red(),
        timestamp=datetime.now(),
    )

    embed.add_field(name=__("logsConfig.embedFields.mention"), value=member.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.name"), value=member.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.id"), value=member.id, inline=True)
    embed.add_field(
        name=__("logsConfig.embedFields.totalMembers"),
        value=__("logsConfig.embedValues.memberCount", count=member.guild.member_count),
        inline=False,
    )

    return embed


def get_voice_state_join_embed(member, after) -> Embed:
    embed = Embed(
        title=__("logsConfig.embedTitles.voiceJoin"),
        color=Color.green(),
        timestamp=datetime.now(),
    )
    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=member.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userName"), value=member.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=member.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.voiceChannelMention"), value=after.channel.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.voiceChannelName"), value=after.channel.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.voiceChannelId"), value=after.channel.id, inline=True)

    return embed


def get_voice_state_leave_embed(member, before) -> Embed:
    embed = Embed(
        title=__("logsConfig.embedTitles.voiceLeave"),
        color=Color.red(),
        timestamp=datetime.now(),
    )
    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=member.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userName"), value=member.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=member.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.voiceChannelMention"), value=before.channel.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.voiceChannelName"), value=before.channel.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.voiceChannelId"), value=before.channel.id, inline=True)

    return embed


def get_voice_state_move_embed(member, before, after) -> Embed:
    embed = Embed(
        title=__("logsConfig.embedTitles.voiceMove"),
        color=Color.blue(),
        timestamp=datetime.now(),
    )
    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=member.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userName"), value=member.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=member.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=__("logsConfig.embedFields.oldVoiceChannelMention"),
        value=before.channel.mention,
        inline=True,
    )
    embed.add_field(name=__("logsConfig.embedFields.oldVoiceChannelName"), value=before.channel.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.oldVoiceChannelId"), value=before.channel.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.newVoiceChannelMention"), value=after.channel.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.newVoiceChannelName"), value=after.channel.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.newVoiceChannelId"), value=after.channel.id, inline=True)

    return embed


def get_member_update_nick_embed(before: Member, after: Member) -> Embed:
    embed = Embed(title=__("logsConfig.embedTitles.nickChange"), color=Color.blue(), timestamp=datetime.now())

    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=after.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userName"), value=after.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.oldNick"), value=before.nick, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.newNick"), value=after.nick, inline=True)

    return embed


def get_member_update_username_embed(before: Member, after: Member) -> Embed:
    embed = Embed(title=__("logsConfig.embedTitles.usernameChange"), color=Color.blue(), timestamp=datetime.now())

    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=after.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(name=__("logsConfig.embedFields.oldName"), value=before.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.newName"), value=after.name, inline=True)

    return embed


def get_member_update_avatar_embed(before: Member, after: Member) -> Embed:
    embed = Embed(title=__("logsConfig.embedTitles.avatarChange"), color=Color.blue(), timestamp=datetime.now())
    if after.avatar is not None:
        embed.set_image(url=after.avatar.url)

    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=after.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userName"), value=after.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=__("logsConfig.embedFields.oldAvatarUrl"),
        value=before.avatar.url if before.avatar else __("logsConfig.embedValues.noOldAvatar"),
        inline=True,
    )
    embed.add_field(
        name=__("logsConfig.embedFields.newAvatarUrl"),
        value=after.avatar.url if after.avatar else __("logsConfig.embedValues.noNewAvatar"),
        inline=True,
    )

    return embed


def get_member_update_banner_embed(before: Member, after: Member) -> Embed:
    embed = Embed(title=__("logsConfig.embedTitles.bannerChange"), color=Color.blue(), timestamp=datetime.now())

    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=after.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userName"), value=after.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=after.id, inline=True)

    create_separator(embed)

    embed.add_field(
        name=__("logsConfig.embedFields.oldBanner"),
        value=before.banner.url if before.banner else __("logsConfig.embedValues.noOldBanner"),
        inline=True,
    )
    embed.add_field(
        name=__("logsConfig.embedFields.newBanner"),
        value=after.banner.url if after.banner else __("logsConfig.embedValues.noNewBanner"),
        inline=True,
    )

    return embed


def get_member_update_roles_embed(before: Member, after: Member) -> Embed:
    embed = Embed(timestamp=datetime.now())

    embed.add_field(name=__("logsConfig.embedFields.userMention"), value=after.mention, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userName"), value=after.name, inline=True)
    embed.add_field(name=__("logsConfig.embedFields.userId"), value=after.id, inline=True)

    create_separator(embed)

    added_roles = [role for role in after.roles if role not in before.roles]
    removed_roles = [role for role in before.roles if role not in after.roles]

    if added_roles:
        embed.title = __("logsConfig.embedTitles.rolesAdded")
        embed.color = Color.green()
        embed.add_field(
            name=__("logsConfig.embedFields.rolesAdded"),
            value=", ".join([role.name for role in added_roles]),
            inline=True,
        )

    if removed_roles:
        embed.title = __("logsConfig.embedTitles.rolesRemoved")
        embed.color = Color.red()
        embed.add_field(
            name=__("logsConfig.embedFields.rolesRemoved"),
            value=", ".join([role.name for role in removed_roles]),
            inline=True,
        )

    return embed
