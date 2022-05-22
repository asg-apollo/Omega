from disnake.ext.commands import Cog
from library.cogs import configuration
from library.db import db


class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member):
        # if not member.bot: db.execute("INSERT OR IGNORE INTO exp (UserID) VALUES (?)", ((member.id,) for member in
        # guild.members for guild in self.guild)) db.execute(f'UPDATE exp SET Username WHERE UserID = "{member.id}"')

        record = db.record("SELECT welcomeModule FROM guildSettings WHERE GuildID = (?)", member.guild.id)
        for onBool in record:
            isFalse = onBool
        if isFalse is False:
            return
        record = db.record("SELECT welcomeChannel FROM guildSettings WHERE GuildID = (?)", member.guild.id)
        for chan in record:
            channel = chan
        if chan is None:
            return

        # channel = self.bot.get_channel(configuration.welcomeChannel)
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
