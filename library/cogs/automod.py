from disnake.ext.commands import Cog
from disnake.ext.commands import command
from ..bot import config


class autoMod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("automod")

    @Cog.listener()
    async def on_message(self, message):

        if message.author.id == 948767251312554095:
            return

        msg = message.content
        channel = message.channel
        with open("C:/Users/Ethan/Documents/GitHub/Omega/library/bot/blacklistedWords.txt", "r") as f:
            blacklistedWords = f.readlines()

        with open("C:/Users/Ethan/Documents/GitHub/Omega/library/bot/blacklistedLinks.txt", "r") as f2:
            blacklistedLinks = f2.read()

        if config.deleteBlacklistedWords:
            for line in blacklistedWords:
                if line.strip() in msg:
                    await message.delete()
                    await channel.send(f"That is a blacklisted word {message.author.mention}.")
        if config.deleteAllLinks:
            if "https://" in msg:
                await message.delete()
                await channel.send(f"That is a blacklisted link {message.author.mention}.")
        if config.deleteBlacklistedLinks:
            if blacklistedLinks in msg:
                await message.delete()
                await channel.send(f"That is a blacklisted link {message.author.mention}.")

        else:
            return


def setup(bot):
    bot.add_cog(autoMod(bot))
