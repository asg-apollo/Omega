from datetime import datetime
from typing import Optional

import disnake
from disnake import Embed, Member, ChannelType, TextChannel
from disnake.ext.commands import Cog
from library.cogs import configuration

from ..db import db


###         Logging Module for Omega Bot Developed By Apollo[Ethan McKinnon]
###         Development Year: Version 0.0.5[2022 May]


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

        record = db.record("SELECT logMemberLeave FROM guilds WHERE GuildID =?", member.guild.id) # Check if logMemberLeave is enabled in the database
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logMemberLeave is disabled, return
            return

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID = (?)", member.guild.id)
        for channel in record:
            channelID = channel

        channel = self.bot.get_channel(channelID)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        # Create and send an embed with the data of the member before they left
        embed = Embed(title="Member Left", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    ###

    ###         Message Logging[STARTS]

    @Cog.listener()
    async def on_message_delete(self, message):
        record = db.record("SELECT logMessages FROM guilds WHERE GuildID =?", message.guild.id) # Checks the database to see if logMessages is enabled in the guild
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logMessages is disabled, return
            return
        if message.author.bot: # If the message was sent by a bot, return
            return

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", message.guild.id) # Select the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # Create and send an embed with data about the deleted message.
        embed = Embed(title="Message Deleted", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_author(name=message.author, icon_url=message.author.display_avatar)
        embed.add_field(name="Author: ", value=message.author.mention)
        embed.add_field(name="Channel: ", value=message.channel.mention)
        embed.add_field(name="Message:", value=message.content)
        embed.set_footer(text=f"Message ID: {message.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_message_edit(self, beforeMessage, afterMessage):
        record = db.record("SELECT logMessages FROM guilds WHERE GuildID =?", beforeMessage.guild.id) # Checks the database to see if logMessages is enabled in the guild
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 0: # If logMessages is disabled, return
            return
        if beforeMessage.author.bot: # If the message was sent by a bot, return
            return

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", beforeMessage.guild.id) # Select the logChannel from the database.
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # Create and send an embed with data about the edited message.
        embed = Embed(title="Message Edited", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.set_author(name=beforeMessage.author, icon_url=beforeMessage.author.display_avatar)
        embed.add_field(name="Author: ", value=beforeMessage.author.mention)
        embed.add_field(name=f"Channel: ",
                        value=beforeMessage.channel.mention + f"[ Jump to Message]({beforeMessage.jump_url})")
        embed.add_field(name="**Before: **", value=beforeMessage.content, inline=False)
        embed.add_field(name="**After: **", value=afterMessage.content, inline=False)
        embed.set_footer(text=f"Message ID: {beforeMessage.id}")
        await channel.send(embed=embed)

    
    async def log_bulk_delete(self, inter, channelObj: TextChannel,amount: int):
        record = db.record("SELECT logMessages FROM guilds WHERE GuildID =?", inter.guild.id) # Checks the database to see if logMessages is enabled in the guild
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 0: # If log messages is disabled, return
            return
        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id) # Select the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # Create and send an embed with the amount of messages deleted, and in which channel
        embed = Embed(title="Bulk Delete", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.set_author(name=inter.guild.name, icon_url=inter.guild.icon)
        embed.add_field(name="Channel: ", value=channelObj.mention, inline=False)
        embed.add_field(name="Amount of messages deleted: ", value=amount, inline=False)
        await channel.send(embed=embed)

    ###         MESSAGE LOGGING[ENDS]

    ###         GUILD LOGS[START]

    @Cog.listener()
    async def on_guild_channel_create(self, createdChannel):
        record = db.record("SELECT logGuildChanges FROM guilds WHERE GuildID =?", createdChannel.guild.id) # Check the database to see if logGuildChanges
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logGuildChanges is disabled, return
            return

        channelType = None
        entry = list(await createdChannel.guild.audit_logs(limit=1).flatten())[0]
        # Determine if the createdChannel is a voice channel or a text channel
        if createdChannel.type == ChannelType.voice:
            channelType = "Voice"
        if createdChannel.type == ChannelType.text:
            channelType = "Text"

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", createdChannel.guild.id) # Select the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # Create and send an embed logging the creation of the channel
        embed = Embed(title=f"{channelType} Channel Created", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.add_field(name="Creator: ", value=entry.user.mention)
        embed.set_author(name=entry.user, icon_url=entry.user.display_avatar)
        embed.add_field(name="Channel Name: ", value=createdChannel.mention)
        embed.set_footer(text=f"Channel ID: {createdChannel.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_guild_channel_delete(self, deletedChannel):
        record = db.record("SELECT logGuildChanges FROM guilds WHERE GuildID =?", deletedChannel.guild.id) # Check the database to see if logGuildChanges is enabled
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logGuildChanges is disabled, return
            return

        channelType = None
        entry = list(await deletedChannel.guild.audit_logs(limit=1).flatten())[0]
        # Determine if the deletedChannel was a voice channel or text channel.
        if deletedChannel.type == ChannelType.voice:
            channelType = "Voice"
        if deletedChannel.type == ChannelType.text:
            channelType = "Text"

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", deletedChannel.guild.id) # Select the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # Create and send an embed logging the channel being deleted
        embed = Embed(title=f"{channelType} Channel Deleted", color=disnake.Color.red(),
                        timestamp=datetime.now())
        embed.add_field(name="Deleter: ", value=entry.user.mention)
        embed.set_author(name=entry.user, icon_url=entry.user.avatar)
        embed.add_field(name="Channel Name: ", value=deletedChannel)
        embed.set_footer(text=f"Channel ID: {deletedChannel.id}")
        await channel.send(embed=embed)


    # YET TO BE IMPLEMENTED [VERSION 0.5.0]
    """
    @Cog.listener()
    async def on_guild_channel_update(self, before, after):
        record = db.record("SELECT logGuildChanges FROM guilds WHERE GuildID =?", before.guild.id)
        for (configBool) in record:
            isFalse = configBool
    
        if isFalse == 0:
            return
        record = db.record("SELECT GuildID FROM guilds WHERE GuildID =?", before.guild.id)
        for (configGuild) in record:
            guild = configGuild
    
        guild = self.bot.get_guild(guild)
        entry = list(await guild.audit_logs(limit=1).flatten())[0]
        embed = Embed(title="Channel Updated", color=disnake.Color.dark_teal())
    
        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", before.guild.id)
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)
    
        if after.name is not before.name:
            embed.add_field(name="Name Before: ", value=before.name)
            embed.add_field(name="Name After: ", value=after.name)
        if after.category is not before.category:
            embed.add_field(name="Old Category: ", value=before.category)
            embed.add_field(name="New Category: ", value=after.category)
        if after.changed_roles:
            return
        else:
            embed.add_field(name="Updater: ", value=entry.user.mention)
            embed.set_footer(text=f"Channel ID: {before.id}")
            embed.set_author(name=entry.user)
            await channel.send(embed=embed)
    """

    ###         GUILD LOGS [END]

    ###         MODERATION LOGS [START]

    async def log_ban(self, inter, member: Member, reason: str):
        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if logModerationActions is enabled
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logModerationActions is disabled, return
            return

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id) # Get the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        memberRoles = (", ".join([str(r.name) for r in member.roles])) # Create a list of the users roles

        # Create and send an embed giving details about the ban
        embed = Embed(title="Member Banned", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_kick(self, inter, member: Member, reason: str,):

        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if logModerationActions is enabled
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logModerationActions is disabled, return
            return

        record = db.record("SELECT dmUserOnKickOrBan FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if dmUserOnKickOrBan is enabled
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 1: # If dmUserOnKickOrBan is enabled, dm the user about the kick.
            await member.send(
                f"You have been kicked from {inter.guild.name} for {reason}. Feel free to join back and follow our rules!")

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id) # Get the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        memberRoles = (", ".join([str(r.name) for r in member.roles])) # Create a list of the members roles

        # Create and send an embed with details about the kick.
        embed = Embed(title="Member Kicked", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_unban(self, inter , memberID: int, reason: str):

        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if logModerationActions is enabled
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logModerationActions is disabled, return
            return

        member = await self.bot.fetch_user(memberID) # Fetch the user object

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id) # Get the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # Create and send an embed with details about the unban.
        embed = Embed(title="Member Unbanned", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_restrict(self, inter, member: Member, duration: int):
        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if logModerationActions is enabled
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logModerationActions is disabled, return
            return

        record = db.record("SELECT dmUserOnKickOrBan FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if dmUserOnKickOrBan is enabled.
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 1: # If dmUserOnKickOrBan is enabled, message the user
            await member.send(
                f"You have been restricted in {inter.guild.name} for {duration}. Once the timer is up feel free to continue talking!")

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id) # Get the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)
        
        # Create and send an embed with information about the restriction.
        embed = Embed(title="Member Restriction Placed", color=disnake.Color.red(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=f"{member.name}#{member.discriminator}", value=chr(173), inline=True)
        embed.set_footer(text=f"ID: {member.id}. Duration: {duration}s")
        await channel.send(embed=embed)

    async def log_unrestrict(self, inter, member: Member, reason: Optional[str]):
        record = db.record("SELECT logModerationActions FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if logModerationActions is enabled
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # If logModerationActions is disabled, return
            return

        record = db.record("SELECT dmUserOnKickOrBan FROM guilds WHERE GuildID =?", member.guild.id) # Check the database to see if dmUserOnKickOrBan is enabled
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 1: # If dmUserOnKickOrBan is enabled, message the user.
            await member.send(
                f"You have been unrestricted in {inter.guild.name}. Feel free to continue talking!")

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id) # Get the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # Create and send an embed with detail about the restriction being lifted.
        embed = Embed(title="Member Restriction Lifted", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar)
        embed.add_field(name=f"{member.name}#{member.discriminator}", value=chr(173), inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    ###

    ### User Logs

    # @Cog.listener()
    # async def on_user_update(self, before, after):
    #     record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", before.guild.id)
    #     for (configChannel) in record:
    #         logChannel = configChannel
    #     channel = self.bot.get_channel(logChannel)
    #     print("Update")

    #     record = db.record("SELECT logUserUpdates FROM guilds WHERE GuildID =?", before.guild.id)
    #     for (configBool) in record:
    #         isFalse = configBool

    #     if isFalse == 0:
    #         return



    #     embed = Embed(title=f"{typeOfChange} Change", color=disnake.Color.dark_teal(), timestamp=datetime.now())
    #     if typeOfChange == "Avatar":
    #         embed.add_field(name="Avatar Before: ", value=f"[Before]({before.avatar})", inline=True)
    #         embed.add_field(name="Avatar After: ", value=f"[After]({after.avatar})", inline=True)
    #         embed.set_author(name=before, icon_url=before.avatar)

    #     elif typeOfChange == "Username":
    #         embed.add_field(name="Username Before: ", value=f"{before.username}", inline=True)
    #         embed.add_field(name="Username After: ", value=f"{after.username}", inline=True)
    #         embed.set_author(name=before, icon_url=before.avatar)

    #     elif typeOfChange == "Discriminator":
    #         embed.add_field(name="Discriminator Before: ", value=before.discriminator)
    #         embed.add_field(name="Discriminator After: ", value=after.discriminator)
    #         embed.set_author(name=before, icon_url=before.avatar)

    #     else:
    #         return
    #     await channel.send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before, after):

        record = db.record("SELECT logUserUpdates FROM guilds WHERE GuildID =?", before.guild.id) # Check the database to see if logUserUpdates is enabled.
        for (configBool) in record:
            isFalse = configBool

        if isFalse == 0: # logUserUpdates is disabled, return
            return

        typeOfChange = "" # Create an empty string defining the type of change that occurs

        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", before.guild.id) # Get the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel
        channel = self.bot.get_channel(logChannel)

        # If any of the users properties change, set the type of change to the change that occured 
        if after.display_name is not before.display_name: 
            typeOfChange = "Nickname"
        if after.avatar is not before.avatar:
            typeOfChange = "Avatar"
        if after.username is not before.username:
            typeOfChange = "Username"
        if after.discriminator is not before.discriminator:
            typeOfChange == "Discriminator"

        # Create and send an embed with details about the change
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
        elif typeOfChange == "Nickname":
            embed.add_field(name="Nickname Before: ", value=before.display_name)
            embed.add_field(name="Nickname After: ", value=after.display_name)
            embed.set_author(name=before, icon_url=before.avatar)
            await channel.send(embed=embed)
        else:
            return
    ###

    ### Economy Logs

    async def give_or_remove_coins_logs(self, inter, authorizer, receiver, amount):
        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                            receiver.id) # Get the recievers balance from the database
        for (balance) in balRecord:
            memberBalance = balance
        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID =?", inter.guild.id) # Get the logChannel from the database
        for (configChannel) in record:
            logChannel = configChannel

        channel = inter.guild.get_channel(logChannel)
        authorizer = inter.guild.get_member(authorizer.id)
        receiver = inter.guild.get_member(receiver.id)

        oldBalance = memberBalance - amount
        newBalance = memberBalance

        # Create and send an embed with details about the transaction.
        embed = Embed(title=f"Coins Changed", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.add_field(name="Authorizer: ", value=authorizer.name, inline=False)
        embed.add_field(name="Receiver: ", value=receiver.name, inline=False)
        embed.add_field(name="Amount Changed: ", value=amount, inline=False)
        embed.add_field(name="Old Balance: ", value=oldBalance, inline=False)
        embed.add_field(name="New Balance: ", value=newBalance, inline=False)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Logs(bot))
