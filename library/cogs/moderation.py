import asyncio
from typing import Optional

import disnake
from disnake import Member, Embed, Interaction
from disnake.ext.commands import Cog, has_permissions, slash_command
from disnake.ext.commands import command
from library.bot import config

from library.cogs import logs
from library.db import db


class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("moderation")

    # Punishment Commands
    @has_permissions(ban_members=True)
    @slash_command(name="ban", description="Bans the mentioned member.")
    async def _ban(self, inter, member: Member, *, reason=''):
        await logs.Logs.log_ban(self, member, reason, config.leaveLogsChannel, inter)
        await member.ban(reason=reason)
        await inter.send("Member Banned.")

    @has_permissions(kick_members=True)
    @slash_command(name="kick", description="Kicks the mentioned member.")
    async def _kick(self, inter, member: Member, *, reason=''):
        await logs.Logs.log_kick(self, member, reason, config.leaveLogsChannel, inter)
        await member.kick(reason=reason)
        await inter.send("Member kicked.")

    @has_permissions(kick_members=True)
    @slash_command(name="restrict",
                   description="Restricts the mentioned member, removing the ability to message for x amount of "
                               "seconds.")
    async def _restricted(self, inter, member: Member, *, duration: int):

        db.execute("INSERT OR IGNORE INTO restricted (UserID) VALUES(?)", member.id)
        db.execute(f"UPDATE restricted SET durationTillUnrestricted = (?) WHERE UserID = (?)", duration, member.id)
        db.commit()

        if duration is None:
            duration = 60

        record = db.record("SELECT restrictedRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (configRole) in record:
            restrictedRole = configRole

        role = disnake.utils.get(inter.guild.roles, name=restrictedRole)

        await logs.Logs.log_restrict(self, member, duration, config.moderationLogsChannel, inter)
        await inter.send(f"{member.mention} has been restricted for {duration}s.")
        await member.add_roles(role)
        await asyncio.sleep(duration)
        await member.remove_roles(role)
        duration = 0
        reason = "Automatic Restriction Lifted"
        await logs.Logs.log_unrestrict(self, member, reason, config.moderationLogsChannel, inter)

    # Punishment Lifting Commands
    @has_permissions(ban_members=True)
    @slash_command(name="unban", description="Unbans the chosen user ID.")
    async def _unban(self, inter, memberID: int, *, reason=''):
        member = await self.bot.fetch_user(memberID)
        banned_users = await self.bot.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.id == member.id:
                await inter.guild.unban(user)
                await logs.Logs.log_unban(self, memberID, reason, config.leaveLogsChannel, inter)
                await inter.send(f"{member.display_name} has been unbanned.")
                return

    @has_permissions(kick_members=True)
    @slash_command(name="unrestrict", description="Unrestricts the mentioned member.")
    async def _unrestrict(self, inter, member: Member, *, reason=''):
        record = db.record("SELECT restrictedRole FROM guildRoles WHERE GuildID =?", inter.guild.id)
        for (configRole) in record:
            restrictedRole = configRole

        role = disnake.utils.get(inter.guild.roles, name=restrictedRole)
        if role in member.roles:
            await inter.send(f"{member.mention} has been unrestricted.")
            await member.remove_roles(role)
            await logs.Logs.log_unrestrict(self, member, reason, config.moderationLogsChannel, inter)
        else:
            await inter.send(f"{member} is not restricted!")

    @has_permissions(manage_messages=True)
    @slash_command(name="clear", description="Deletes the inputted amount of messages in a channel.")
    async def _clear(self, inter, amount: int):
        await inter.channel.purge(limit=amount, bulk=True)
        msg = await inter.response.send_message(f"{amount} messages have been deleted in {inter.channel.mention}!")

    @_clear.error
    async def _clear_error(self, inter, exc):
        print(exc)


def setup(bot):
    bot.add_cog(Moderation(bot))
