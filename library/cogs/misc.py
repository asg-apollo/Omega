from datetime import datetime

import disnake
from disnake import TextChannel, Role, Embed, Interaction
from disnake.ext.commands import command, Cog, has_permissions, CheckFailure, slash_command

from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    # OLD FUNCTIONALITY (0.0.5)
    # @slash_command(name="prefix", description="Change the bots prefix.")
    # @has_permissions(manage_guild=True)
    # async def change_prefix(self, inter, new: str):
    #     if len(new) > 5:
    #         await inter.send("The prefix can not be more than 5 characters in length.")
    #     else:
    #         db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, inter.guild.id)
    #         await inter.send(f"Prefix set to {new}.")
    #
    # @change_prefix.error
    # async def change_prefix_error(self, inter, exc):
    #     if isinstance(exc, CheckFailure):
    #         await inter.send("You need the Manage Server permission to do that.")

    @slash_command(name="bot-stats", description="Stats about the bot!")
    async def botStats(self, inter):
        guildCount = 0
        for guild in self.bot.guilds:
            guildCount += 1
        embed = Embed(title="__Bot Stats__", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.add_field(name="Server Count: ", value=guildCount)
        embed.set_thumbnail(self.bot.user.display_avatar)
        await inter.response.send_message(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))
