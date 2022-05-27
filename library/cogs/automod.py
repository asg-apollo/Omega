from disnake.ext.commands import Cog
from library.db import db


###         AutoModeration Module for Omega Bot Developed By Apollo[Ethan McKinnon]
###         Development Year: Version 0.5.0[2022 May]


class autoMod(Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("automod") # Readys up the AutoModeration module 

    @Cog.listener()
    async def on_message(self, message):

        if message.author.bot == True: # If the message was sent by a bot, ignore it
            return

        msg = message.content 
        channel = message.channel
        with open("./library/bot/blacklistedWords.txt", "r") as f: # Opens & reads the blacklisted words text file.
            blacklistedWords = f.readlines()

        with open("./library/bot/blacklistedLinks.txt", "r") as f2: # Opens & reads the blacklisted links text file.
            blacklistedLinks = f2.read()

        record = db.record("SELECT deleteBlacklistedWords FROM guilds WHERE GuildID =?", message.guild.id) # Checks the settings database to see if deleting blacklisted words is enabled for the guild the message was sent in.
        for (configBool) in record:
            isTrue = configBool

        if isTrue == 1: # If deleting blacklisted words is enabled, continue
            for line in blacklistedWords: # Checks if the message contains a blacklisted word
                if line.strip() in msg:
                    await message.delete()
                    await channel.send(f"That is a blacklisted word {message.author.mention}.")
        else:
            pass

        record = db.record("SELECT deleteAllLinks FROM guilds WHERE GuildID =?", message.guild.id) # Checks the setting database to see if deleting all links is enabled for the guild the message was sent in.
        for (configBool) in record:
            isTrue = configBool

        if isTrue == 1: # If deleting all links is enabled, continue
            if "https://" in msg: # Checks if message contatins "https://"
                await message.delete()
                await channel.send(f"That is a blacklisted link {message.author.mention}.")
        else:
            pass

        record = db.record("SELECT deleteBlacklistedLinks FROM guilds WHERE GuildID =?", message.guild.id) # Checks the setting database to see if deleting blacklisted links is enabled for the guild the message was sent in.
        for (configBool) in record:
            isTrue = configBool

        if isTrue == 1: # If deleting blacklisted links is enabled, continue
            if blacklistedLinks in msg: # If message contains a blacklisted link, continue
                await message.delete()
                await channel.send(f"That is a blacklisted link {message.author.mention}.")
        else:
            return


def setup(bot):
    bot.add_cog(autoMod(bot))
