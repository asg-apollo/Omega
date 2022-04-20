from datetime import datetime
from typing import Optional

import discord
from discord import Embed, Member, Colour
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

    @Cog.listener()
    async def on_member_leave(self, member):
        channel = self.bot.get_channel(config.leaveLogsChannel)

        memberRoles = (", ".join([str(r.name) for r in member.roles]))

        embed = Embed(title="Member Left", color=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    @Cog.listener()
    async def on_message_delete(self, message):
        guild = self.bot.get_guild(889946079188095006)
        deleter = list(await guild.audit_logs(limit=1).flatten())[0]
        user = self.bot.get_user(deleter.user.id)
        channel = self.bot.get_channel(config.moderationLogsChannel)
        await channel.send(user.avatar_url)
        print(message.content, message.author, message.id)


    async def log_ban(self, member: Member, reason: str, channel: int, ctx):
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

        member = await self.bot.fetch_user(memberID)
        channel = self.bot.get_channel(channel)

        embed = Embed(title="Member Unbanned", color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=member.mention, value=f"{member.name}#{member.discriminator}", inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)

    async def log_restrict(self, member: Member, duration: int, channel: int, ctx):
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
        if config.dmUserOnModerationAction:
            await member.send(
                f"You have been unrestricted in {ctx.guild.name}. Feel free to continue talking!")

        channel = self.bot.get_channel(channel)

        embed = Embed(title="Member Restriction Lifted", color=discord.Color.green(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=f"{member.name}#{member.discriminator}", value=chr(173), inline=True)
        embed.set_footer(text=f"ID: {member.id}. Reason: {reason}")
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Logs(bot))
