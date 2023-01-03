import asyncio
from datetime import datetime
from http.client import HTTPException
import disnake
from disnake import Member, Embed, Role, HTTPException, Forbidden
from disnake.ext import commands
from disnake.ext.commands import Cog, has_permissions, slash_command, MissingRole, MissingPermissions, guild_only
from library.cogs import logs
from library.db import db


###         Moderation Module for Omega Bot Developed By Apollo[Ethan McKinnon]
###         Development Year: Version 0.0.5[2022 May]


class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.modRole = ''

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("moderation")

    # region Punishment Commands

    # Bans the mentioned member with an optional reason. Requires the ban_members permission.
    @guild_only()
    @has_permissions(ban_members=True)
    @slash_command(name="ban", description="Bans the mentioned member.")
    async def _ban(self, inter, member: Member, *, reason=''):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0":  # If the moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        await logs.Logs.log_ban(self, inter, member, reason)  # Log the ban to the dedicated logs channel.
        await member.ban(reason=reason)  # Ban the member with the select reason.
        await inter.send(f"{member} Banned.")

    # Kicks the mentioned member with an optional reason. Requires the kick_members permission.
    @guild_only()
    @has_permissions(kick_members=True)
    @slash_command(name="kick", description="Kicks the mentioned member.")
    async def _kick(self, inter, member: Member, *, reason=''):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0":  # If moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        await member.kick(reason=reason)  # Kick the member with the given reason.
        await logs.Logs.log_kick(self, inter, member, reason)  # Log the kick to the designated logs channel.
        await inter.send(f"{member} kicked.")


    # @guild_only()
    # @slash_command(name="warn", description="Warns the mentioned member.")
    # async def _warn(self, inter, member: Member, reason=""):
    #     # TODO |NEEDS TO BE DONE BY 2022-06-06 | Warn a member, send a dm to the member, log the warn, add warn to warn counter db.
    #     pass

    # endregion

    # region PUNISHMENT LIFTING COMMANDS

    # Unbans the member with the provided id with an optional reason. Requires the ban_members permission.
    @guild_only()
    @has_permissions(ban_members=True)
    @slash_command(name="unban", description="Unbans the chosen user ID.")
    async def _unban(self, inter, memberID: int, *, reason=''):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0":  # If moderation module is disabled, send an error and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        member = await self.bot.fetch_user(memberID)  # Fetch the user object by ID
        banned_users = await self.bot.guild.bans()  # Grabs the guilds ban list
        for ban_entry in banned_users:  # Checks if the user id is in the ban list.
            user = ban_entry.user
            if user.id == member.id:  # If members id is in the ban list, continue
                await inter.guild.unban(user)  # Unban the member
                await logs.Logs.log_unban(self, inter, memberID, reason)  # Log the unban in the designated logs channel.
                await inter.send(f"{member.display_name} has been unbanned.")
                return


    # Clears the specified amount of messages. Requires the manage_messages permission. Cannot delete messages over 14 days.
    @guild_only()
    @has_permissions(manage_messages=True)
    @slash_command(name="clear", description="Deletes the inputted amount of messages in a channel.")
    async def _clear(self, inter, amount: int):
        await inter.response.defer()
        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0":  # If the moderation module is disabled, send a error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return
        mgs = []  # Create a empty list of messages
        await inter.delete_original_message()
        async for x in inter.channel.history(limit=amount):
            mgs.append(x)

        try:
            await inter.channel.delete_messages(mgs)  # Delete the list of messages
        except:
            raise
            return

        await inter.channel.send(f"{amount} messages have been deleted in {inter.channel.mention}!", delete_after=5)
        await logs.Logs.log_bulk_delete(self, inter, inter.channel, amount)

    # endregion PUNISHMENT LIFTING COMMANDS

    # region ERROR HANDLING

    @_ban.error
    async def _ban_error(self, inter, exc):
        if isinstance(exc, MissingPermissions):
            await inter.response.send_message("You are missing the Ban Members Permission.")

    @_kick.error
    async def _kick_error(self, inter, exc):
        if isinstance(exc, MissingPermissions):
            await inter.response.send_message("You are missing the Kick Members Permission.")
        if isinstance(exc, commands.BotMissingPermissions):
            await inter.channel.send("I do not have permission to do that.")
        else:
            print(exc)

    @_clear.error
    async def _clear_error(self, inter, exc):
        print(exc)
        if isinstance(exc, disnake.HTTPException):
            await inter.channel.send("Messages over 14 days old cannot be cleared.")
        if exc == MissingPermissions:
            await inter.channel.send("I am missing the required permissions!")
        else:
            await inter.channel.send("An error occurred.")

    # endregion


def setup(bot):
    bot.add_cog(Moderation(bot))
