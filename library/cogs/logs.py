from datetime import datetime
from typing import Optional

import discord
from discord import Embed, Member, Colour, ChannelType
from discord.ext.commands import Cog
from discord.ext.commands import command
from ..bot import config

from ..db import db


class Logs(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("logs")

    ### Leave Logs
    @Cog.listener()
    async def on_member_leave(self, member):

        if not config.logMemberLeave:
            return

        channel = self.bot.get_channel(config.leaveLogsChannel)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        embed = Embed(title="Member Left", color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    ###

    ### Message Logs
    @Cog.listener()
    async def on_message_delete(self, message):
        if not config.logMessages:
            return

        channel = self.bot.get_channel(config.moderationLogsChannel)
        embed = Embed(title="Message Deleted", color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name="Author: ", value=message.author.mention)
        embed.add_field(name="Channel: ", value=message.channel.mention)
        embed.add_field(name="Message:", value=message.content)
        embed.set_footer(text=f"Message ID: {message.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, beforeMessage, afterMessage):
        if not config.logMessages:
            return

        channel = self.bot.get_channel(config.moderationLogsChannel)
        embed = Embed(title="Message Edited", color=discord.Color.dark_teal(), timestamp=datetime.utcnow())
        embed.set_author(name=beforeMessage.author, icon_url=beforeMessage.author.avatar_url)
        embed.add_field(name="Author: ", value=beforeMessage.author.mention)
        embed.add_field(name=f"Channel: ",
                        value=beforeMessage.channel.mention + f"[ Jump to Message]({beforeMessage.jump_url})")
        embed.add_field(name="**Before: **", value=beforeMessage.content, inline=False)
        embed.add_field(name="**After: **", value=afterMessage.content, inline=False)
        embed.set_footer(text=f"Message ID: {beforeMessage.id}")
        await channel.send(embed=embed)

    ###

    ## Guild Logs

    @Cog.listener()
    async def on_guild_channel_create(self, createdChannel):
        if not config.logGuildChanges:
            return

        guild = self.bot.get_guild(889946079188095006)
        channelType = None
        entry = list(await guild.audit_logs(limit=1).flatten())[0]
        if createdChannel.type == ChannelType.voice:
            channelType = "Voice"
        if createdChannel.type == ChannelType.text:
            channelType = "Text"

        channel = self.bot.get_channel(config.moderationLogsChannel)
        embed = Embed(title=f"{channelType} Channel Created", color=discord.Color.dark_teal(), timestamp=datetime.utcnow())
        embed.add_field(name="Creator: ", value=entry.user.mention)
        embed.set_author(name=entry.user, icon_url=entry.user.avatar_url)
        embed.add_field(name="Channel Name: ", value=createdChannel.mention)
        embed.set_footer(text=f"Channel ID: {createdChannel.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_channel_delete(self, deletedChannel):
        if not config.logGuildChanges:
            return

        guild = self.bot.get_guild(889946079188095006)
        channelType = None
        entry = list(await guild.audit_logs(limit=1).flatten())[0]
        if deletedChannel.type == ChannelType.voice:
            channelType = "Voice"
        if deletedChannel.type == ChannelType.text:
            channelType = "Text"

        channel = self.bot.get_channel(config.moderationLogsChannel)
        embed = Embed(title=f"{channelType} Channel Deleted", color=discord.Color.red(),
                      timestamp=datetime.utcnow())
        embed.add_field(name="Deleter: ", value=entry.user.mention)
        embed.set_author(name=entry.user, icon_url=entry.user.avatar_url)
        embed.add_field(name="Channel Name: ", value=deletedChannel)
        embed.set_footer(text=f"Channel ID: {deletedChannel.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if not config.logGuildChanges:
            return
        guild = self.bot.get_guild(889946079188095006)
        entry = list(await guild.audit_logs(limit=1).flatten())[0]
        embed = Embed(title="Channel Updated", color=discord.Color.dark_teal())
        channel = self.bot.get_channel(config.moderationLogsChannel)
        if after.name is not before.name:
            embed.add_field(name="Name Before: ", value=before.name)
            embed.add_field(name="Name After: ", value=after.name)
        if after.category is not before.category:
            embed.add_field(name="Old Category: ", value=before.category)
            embed.add_field(name="New Category: ", value=after.category)
        if after.changed_roles:
            return
        else:
            print("doneso")
            embed.add_field(name="Updater: ", value=entry.user.mention)
            embed.set_footer(text=f"Channel ID: {before.id}")
            embed.set_author(name=entry.user, icon_url=entry.user.avatar_url)
            await channel.send(embed=embed)
    ###

    ### Moderation Logs

    async def log_ban(self, member: Member, reason: str, channel: int, ctx):
        if not config.logModerationActions:
            return

        if config.dmUserOnKickOrBan:
            await member.send(f"You have been banned from {ctx.guild.name} for {reason}")

        channel = self.bot.get_channel(channel)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        embed = Embed(title="Member Banned", color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_kick(self, member: Member, reason: str, channel: int, ctx):

        if not config.logModerationActions:
            return
        if config.dmUserOnKickOrBan:
            await member.send(
                f"You have been kicked from {ctx.guild.name} for {reason}. Feel free to join back and follow our rules!")

        channel = self.bot.get_channel(channel)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        embed = Embed(title="Member Kicked", color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_unban(self, memberID: int, reason: str, channel: int, ctx):

        if not config.logModerationActions:
            return

        member = await self.bot.fetch_user(memberID)
        channel = self.bot.get_channel(channel)

        embed = Embed(title="Member Unbanned", color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_restrict(self, member: Member, duration: int, channel: int, ctx):
        if not config.logModerationActions:
            return

        if config.dmUserOnModerationAction:
            await member.send(
                f"You have been restricted in {ctx.guild.name} for {duration}.Once the timer is up feel free to continue talking!")

        channel = self.bot.get_channel(channel)

        embed = Embed(title="Member Restriction Placed", color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=f"{member.name}#{member.discriminator}", value=chr(173), inline=True)
        embed.set_footer(text=f"ID: {member.id}. Duration: {duration}s")
        await channel.send(embed=embed)

    async def log_unrestrict(self, member: Member, reason: Optional[str], channel: int, ctx):
        if not config.logModerationActions:
            return

        if config.dmUserOnModerationAction:
            await member.send(
                f"You have been unrestricted in {ctx.guild.name}. Feel free to continue talking!")

        channel = self.bot.get_channel(channel)

        embed = Embed(title="Member Restriction Lifted", color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=f"{member.name}#{member.discriminator}", value=chr(173), inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)
    ###

    ### User Logs

    @Cog.listener()
    async def on_user_update(self, before, after):
        channel = self.bot.get_channel(config.moderationLogsChannel)
        if config.logAvatarChanges:
            if after.avatar_url is not before.avatar_url:
                typeOfChange = "Avatar"

        embed = Embed(title=f"{typeOfChange} Change", color=discord.Color.dark_teal(), timestamp=datetime.utcnow())
        if typeOfChange == "Avatar":
            embed.add_field(name="Avatar Before: ", value=f"[Before]({before.avatar_url})", inline=True)
            embed.add_field(name="Avatar After: ", value=f"[After]({after.avatar_url})", inline=True)
            embed.set_author(name=before, icon_url=before.avatar_url)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logs(bot))
