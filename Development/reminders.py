from disnake.ext.commands import Cog
from disnake.ext.commands import command


class reminders(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reminders")


def setup(bot):
    bot.add_cog(reminders(bot))