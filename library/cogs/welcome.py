from sqlite3 import IntegrityError

from discord.ext.commands import Cog
from discord.ext.commands import command
from ..bot import config

from ..db import db

class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        # if not member.bot:
        #     # db.execute("INSERT OR IGNORE INTO exp (UserID) VALUES (?)", ((member.id,) for member in guild.members for guild in self.guild))
        #     # db.execute(f'UPDATE exp SET Username WHERE UserID = "{member.id}"')
        channel = self.bot.get_channel(config.welcomeChannel)
        await channel.send(f"Welcome to {member.guild.name} {member.mention}! Take a look at the rules!")

    @Cog.listener()
    async def on_member_leave(self, member):
        pass


    # @on_member_join.error
    # async def on_member_join_error(self, exc):
    #     if isinstance(exc, IntegrityError):
    #         print("Member already in the database!")

def setup(bot):
    bot.add_cog(Welcome(bot))