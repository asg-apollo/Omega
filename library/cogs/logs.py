from datetime import datetime
from typing import Optional

import disnake
from discord.ext.commands import bot
from disnake import Embed, Member, Colour, ChannelType
from disnake.ext.commands import Cog
from disnake.ext.commands import command
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

        record = db.record("SELECT logMemberLeave FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        channel = self.bot.get_channel(config.leaveLogsChannel)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        embed = Embed(title="Member Left", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    ###

    ### Message Logs
    @Cog.listener()
    async def on_message_delete(self, message):
        record = db.record("SELECT logMessages FROM guilds WHERE GuildID =?", message.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return
        if message.author.bot:
            return

        channel = self.bot.get_channel(config.moderationLogsChannel)
        embed = Embed(title="Message Deleted", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_author(name=message.author, icon_url=message.author.display_avatar)
        embed.add_field(name="Author: ", value=message.author.mention)
        embed.add_field(name="Channel: ", value=message.channel.mention)
        embed.add_field(name="Message:", value=message.content)
        embed.set_footer(text=f"Message ID: {message.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, beforeMessage, afterMessage):
        record = db.record("SELECT logMessages FROM guilds WHERE GuildID =?", beforeMessage.guild.id)
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 0:
            return
        if beforeMessage.author.bot:
            return

        channel = self.bot.get_channel(config.moderationLogsChannel)
        embed = Embed(title="Message Edited", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.set_author(name=beforeMessage.author, icon_url=beforeMessage.author.display_avatar)
        embed.add_field(name="Author: ", value=beforeMessage.author.mention)
        embed.add_field(name=f"Channel: ",
                        value=beforeMessage.channel.mention + f"[ Jump to Message]({beforeMessage.jump_url})")
        embed.add_field(name="**Before: **", value=beforeMessage.content, inline=False)
        embed.add_field(name="**After: **", value=afterMessage.content, inline=False)
        embed.set_footer(text=f"Message ID: {beforeMessage.id}")
        await channel.send(embed=embed)

    async def log_bulk_delete(self, inter, amount: int):
        record = db.record("SELECT logMessages FROM guilds WHERE GuildID =?", inter.guild.id)
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 0:
            return
        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)
        embed = Embed(title="Bulk Delete", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.set_author(name=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Amount of messages deleted: ", value=amount)
        await channel.send(embed=embed)

    ###

    ## Guild Logs

    @Cog.listener()
    async def on_guild_channel_create(self, createdChannel):
        record = db.record("SELECT logGuildChanges FROM guilds WHERE GuildID =?", createdChannel.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        record = db.record("SELECT GuildID FROM guilds WHERE GuildID =?", createdChannel.guild.id)
        for (configGuild) in record:
            guild = configGuild

        guild = self.bot.get_guild(guild)

        channelType = None
        entry = list(await guild.audit_logs(limit=1).flatten())[0]
        if createdChannel.type == ChannelType.voice:
            channelType = "Voice"
        if createdChannel.type == ChannelType.text:
            channelType = "Text"

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", createdChannel.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        embed = Embed(title=f"{channelType} Channel Created", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.add_field(name="Creator: ", value=entry.user.mention)
        embed.set_author(name=entry.user, icon_url=entry.user.display_avatar)
        embed.add_field(name="Channel Name: ", value=createdChannel.mention)
        embed.set_footer(text=f"Channel ID: {createdChannel.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_channel_delete(self, deletedChannel):
        record = db.record("SELECT logGuildChanges FROM guilds WHERE GuildID =?", deletedChannel.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        record = db.record("SELECT GuildID FROM guilds WHERE GuildID =?", deletedChannel.guild.id)
        for (configGuild) in record:
            guild = configGuild

        guild = self.bot.get_guild(guild)
        channelType = None
        entry = list(await guild.audit_logs(limit=1).flatten())[0]
        if deletedChannel.type == ChannelType.voice:
            channelType = "Voice"
        if deletedChannel.type == ChannelType.text:
            channelType = "Text"

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", deletedChannel.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        embed = Embed(title=f"{channelType} Channel Deleted", color=disnake.Color.red(),
                      timestamp=datetime.now())
        embed.add_field(name="Deleter: ", value=entry.user.mention)
        embed.set_author(name=entry.user, icon_url=entry.user.avatar)
        embed.add_field(name="Channel Name: ", value=deletedChannel)
        embed.set_footer(text=f"Channel ID: {deletedChannel.id}")
        await channel.send(embed=embed)

    #on_guild_updates
    # @Cog.listener()
    # async def on_guild_channel_update(self, before, after):
    #     record = db.record("SELECT logGuildChanges FROM guilds WHERE GuildID =?", before.guild.id)
    #     for (configBool) in record:
    #         isFalse = configBool
    #
    #     if isFalse == 0:
    #         return
    #     record = db.record("SELECT GuildID FROM guilds WHERE GuildID =?", before.guild.id)
    #     for (configGuild) in record:
    #         guild = configGuild
    #
    #     guild = self.bot.get_guild(guild)
    #     entry = list(await guild.audit_logs(limit=1).flatten())[0]
    #     embed = Embed(title="Channel Updated", color=disnake.Color.dark_teal())
    #
    #     record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", before.guild.id)
    #     for (configChannel) in record:
    #         logChannel = configChannel
    #     channel = self.bot.get_channel(logChannel)
    #
    #     if after.name is not before.name:
    #         embed.add_field(name="Name Before: ", value=before.name)
    #         embed.add_field(name="Name After: ", value=after.name)
    #     if after.category is not before.category:
    #         embed.add_field(name="Old Category: ", value=before.category)
    #         embed.add_field(name="New Category: ", value=after.category)
    #     if after.changed_roles:
    #         return
    #     else:
    #         embed.add_field(name="Updater: ", value=entry.user.mention)
    #         embed.set_footer(text=f"Channel ID: {before.id}")
    #         embed.set_author(name=entry.user)
    #         await channel.send(embed=embed)

    ###

    ### Moderation Logs##

    async def log_ban(self, member: Member, reason: str, channel: int, ctx):
        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        if config.dmUserOnKickOrBan:
            await member.send(f"You have been banned from {ctx.guild.name} for {reason}")

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", ctx.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        embed = Embed(title="Member Banned", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_kick(self, member: Member, reason: str, channel: int, ctx):

        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return
        record = db.record("SELECT dmUserOnKickOrBan FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 1:
            await member.send(
                f"You have been kicked from {ctx.guild.name} for {reason}. Feel free to join back and follow our rules!")

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", ctx.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        embed = Embed(title="Member Kicked", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_unban(self, memberID: int, reason: str, channel: int, ctx):

        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        member = await self.bot.fetch_user(memberID)
        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", ctx.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        embed = Embed(title="Member Unbanned", color=disnake.Color.green(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_restrict(self, member: Member, duration: int, channel: int, ctx):
        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        record = db.record("SELECT dmUserOnKickOrBan FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 1:
            await member.send(
                f"You have been restricted in {ctx.guild.name} for {duration}.Once the timer is up feel free to continue talking!")

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", ctx.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        embed = Embed(title="Member Restriction Placed", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=f"{member.name}#{member.discriminator}", value=chr(173), inline=True)
        embed.set_footer(text=f"ID: {member.id}. Duration: {duration}s")
        await channel.send(embed=embed)

    async def log_unrestrict(self, member: Member, reason: Optional[str], channel: int, ctx):
        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        record = db.record("SELECT dmUserOnKickOrBan FROM guilds WHERE GuildID =?", member.guild.id)
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 1:
            await member.send(
                f"You have been unrestricted in {ctx.guild.name}. Feel free to continue talking!")

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", ctx.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        embed = Embed(title="Member Restriction Lifted", color=disnake.Color.green(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=f"{member.name}#{member.discriminator}", value=chr(173), inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    ###

    ### User Logs

    @Cog.listener()
    async def on_user_update(self, before, after):
        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", before.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)
        print("Update")

        record = db.record("SELECT logUserUpdates FROM guilds WHERE GuildID =?", before.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        if after.avatar is not before.avatar:
            typeOfChange = "Avatar"

        if after.username is not before.username:
            typeOfChange = "Username"

        if after.discriminator is not before.discriminator:
            typeOfChange == "Discriminator"

        embed = Embed(title=f"{typeOfChange} Change", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        if typeOfChange == "Avatar":
            embed.add_field(name="Avatar Before: ", value=f"[Before]({before.avatar})", inline=True)
            embed.add_field(name="Avatar After: ", value=f"[After]({after.avatar})", inline=True)
            embed.set_author(name=before, icon_url=before.avatar)

        elif typeOfChange == "Username":
            embed.add_field(name="Username Before: ", value=f"{before.username}", inline=True)
            embed.add_field(name="Username After: ", value=f"{after.username}", inline=True)
            embed.set_author(name=before, icon_url=before.avatar)

        elif typeOfChange == "Discriminator":
            embed.add_field(name="Discriminator Before: ", value=before.discriminator)
            embed.add_field(name="Discriminator After: ", value=after.discriminator)
            embed.set_author(name=before, icon_url=before.avatar)

        else:
            return
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):

        record = db.record("SELECT logUserUpdates FROM guilds WHERE GuildID =?", before.guild.id)
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0:
            return

        typeOfChange = ""

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", before.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        if after.display_name is not before.display_name:
            typeOfChange = "Nickname"

        embed = Embed(title=f"{typeOfChange} Change", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        if typeOfChange == "Nickname":
            embed.add_field(name="Nickname Before: ", value=f"{before.nick}", inline=True)
            if before.nick == after.nick:
                return
            else:
                if after.nick is None:
                    nickname = after.display_name
                else:
                    nickname = after.nick
                embed.add_field(name="Nickname After: ", value=f"{nickname}", inline=True)
                embed.set_author(name=before, icon_url=before.avatar)
                await channel.send(embed=embed)
        else:
            return


def setup(bot):
    bot.add_cog(Logs(bot))
