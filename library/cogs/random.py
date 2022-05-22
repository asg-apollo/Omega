import random

from disnake.ext.commands import Cog, slash_command
from disnake.ext.commands import command


class randomModule(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("random")

    @slash_command(name="random-member")
    async def randomMember(self, inter):
        chosenMember = random.choice(inter.guild.members)
        await inter.response.send_message(f"The chosen member is {chosenMember.mention}")


def setup(bot):
    bot.add_cog(randomModule(bot))