from disnake import TextChannel, Role
from disnake.ext.commands import command, Cog, has_permissions, CheckFailure, slash_command

from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="prefix", description="Change the bots prefix.")
    @has_permissions(manage_guild=True)
    async def change_prefix(self, inter, new: str):
        if len(new) > 5:
            await inter.send("The prefix can not be more than 5 characters in length.")
        else:
            db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, inter.guild.id)
            await inter.send(f"Prefix set to {new}.")

    @slash_command(name="setLogChannel", description="Setup the bot.")
    @has_permissions(manage_guild=True)
    async def setLogsChannel(self, inter, logs_channel: TextChannel):
        db.execute(f"UPDATE guildSettings SET logChannel = (?) WHERE GuildID = (?)", logs_channel.id, inter.guild.id)
        db.commit()
        await inter.send(f"Logs channel set to {logs_channel.mention}.")

    @change_prefix.error
    async def change_prefix_error(self, inter, exc):
        if isinstance(exc, CheckFailure):
            await inter.send("You need the Manage Server permission to do that.")

    @setLogsChannel.error
    async def setLogsChannel_error(self, inter, exc):
        if isinstance(exc, CheckFailure):
            await inter.send("You need the Manage Server permission to do that.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))
