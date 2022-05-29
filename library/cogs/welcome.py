from datetime import datetime

import disnake
from disnake import Embed
from disnake.ext.commands import Cog
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

        record = db.record("SELECT welcomeModule FROM guildSettings WHERE GuildID = (?)", member.guild.id)  # Check the database to see if the welcomeModule is enabled
        for onBool in record:
            isFalse = onBool
        if isFalse == 0:  # If the welcomeModule is disabled, return
            return
        record = db.record("SELECT welcomeChannel FROM guildSettings WHERE GuildID = (?)", member.guild.id)  # Select the welcomeChannel from the database
        for chan in record:
            channel = chan
        if chan is None:
            return

        channel = member.guild.get_channel(channel)

        await channel.send(f"Welcome to {member.guild.name} {member.mention}! Be sure to take a look at the rules!")

    @Cog.listener()
    async def on_member_remove(self, member):
        print(member)
        record = db.record("SELECT welcomeModule FROM guildSettings WHERE GuildID = (?)", member.guild.id)  # Check the database to see if the welcomeModule is enabled
        for onBool in record:
            isFalse = onBool
        if isFalse == 0:  # If the welcomeModule is disabled, return
            return
        record = db.record("SELECT logChannel FROM guildSettings WHERE GuildID = (?)", member.guild.id)  # Select the welcomeChannel from the database
        for chan in record:
            channel = chan
        if chan is None:
            return


        channel = member.guild.get_channel(channel)
        memberRoles = (", ".join([str(r.name) for r in member.roles]))  # Create a list of the members roles

        # Create and send an embed with details about who left
        embed = Embed(title="Member Left", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        if member.avatar is not None:
            embed.set_thumbnail(url=member.avatar)

        embed.add_field(name="User Info" , value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Roles Held:", value=memberRoles, inline=True)
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed)

    # @on_member_join.error
    # async def on_member_join_error(self, exc):
    #     if isinstance(exc, IntegrityError):
    #         print("Member already in the database!")


def setup(bot):
    bot.add_cog(Welcome(bot))
