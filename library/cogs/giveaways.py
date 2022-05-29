import random

from disnake.ext.commands import Cog, slash_command
from disnake.ext.commands import command


class giveaways(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("giveaways")

    @slash_command(name="random-member")
    async def randomMember(self, inter):
        chosenMember = random.choice(inter.guild.members)
        await inter.response.send_message(f"The chosen member is {chosenMember.mention}")

    # TODO Create a giveaway system


    # @slash_command(name="start-giveaway")
    # async def startGiveaway(self, inter, giveaway_title: str, prize: str):
    #     pass


def setup(bot):
    bot.add_cog(giveaways(bot))