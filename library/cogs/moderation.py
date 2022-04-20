import asyncio
from typing import Optional

import discord
from discord import Member
from discord.ext.commands import Cog, has_permissions
from discord.ext.commands import command
from ..bot import config

from . import logs
from ..db import db


class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("moderation")

    # Punishment Commands
    @has_permissions(ban_members=True)
    @command(name="ban", brief="Bans the mentioned member.")
    async def _ban(self, ctx, member: Member, *, reason: Optional[str]):
        await logs.Logs.log_ban(self, member, reason, config.leaveLogsChannel, ctx)
        await member.ban(reason=reason)
        await ctx.send("Member Banned.")

    @has_permissions(kick_members=True)
    @command(name="kick", brief="Kicks the mentioned member.")
    async def _kick(self, ctx, member: Member, *, reason: Optional[str]):
        await logs.Logs.log_kick(self, member, reason, config.leaveLogsChannel, ctx)
        await member.kick(reason=reason)
        await ctx.send("Member kicked.")

    @has_permissions(kick_members=True)
    @command(name="restrict",
             brief="Restricts the mentioned member, removing the ability to message for x amount of seconds.")
    async def _restricted(self, ctx, member: Member, *, duration: Optional[int]):

        db.execute("INSERT OR IGNORE INTO restricted (UserID) VALUES(?)", member.id)
        db.execute(f"UPDATE restricted SET durationTillUnrestricted = (?) WHERE UserID = (?)", duration, member.id)
        db.commit()


        if duration is None:
            duration = 60

        role = discord.utils.get(ctx.guild.roles, name=config.restrictedRole)

        await logs.Logs.log_restrict(self, member, duration, config.moderationLogsChannel, ctx)
        await ctx.send(f"{member.mention} has been restricted for {duration}s.")
        await member.add_roles(role)
        await asyncio.sleep(duration)
        await member.remove_roles(role)
        duration = 0
        reason = "Automatic Restriction Lifted"
        await logs.Logs.log_unrestrict(self, member, reason, config.moderationLogsChannel, ctx)

    # Punishment Lifting Commands
    @has_permissions(ban_members=True)
    @command(name="unban", brief="Unbans the chosen ID.")
    async def _unban(self, ctx, memberID: int, *, reason: Optional[str]):
        member = await self.bot.fetch_user(memberID)
        banned_users = await self.bot.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.id == member.id:
                await ctx.guild.unban(user)
                await logs.Logs.log_unban(self, memberID, reason, config.leaveLogsChannel, ctx)
                await ctx.send(f"{member.display_name} has been unbanned.")
                return

    @has_permissions(kick_members=True)
    @command(name="unrestrict")
    async def _unrestrict(self, ctx, member: Member, *, reason: Optional[str]):
        role = discord.utils.get(ctx.guild.roles, name=config.restrictedRole)
        if role in member.roles:
            await ctx.send(f"{member.mention} has been unrestricted.")
            await member.remove_roles(role)
            await logs.Logs.log_unrestrict(self, member, reason, config.moderationLogsChannel,ctx)
        else:
            await ctx.send(f"{member} is not restricted!")


def setup(bot):
    bot.add_cog(Moderation(bot))
