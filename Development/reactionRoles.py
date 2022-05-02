import disnake
from disnake import Emoji, TextChannel
from disnake.ext.commands import Cog, slash_command
from disnake.ext.commands import command


class reactionRoles(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.msg = None

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reactionRoles")

    @slash_command(name="createReactionRole")
    async def createReactionRole(self, inter, channel: TextChannel, reaction1:str, reaction2: str, message: str):
        self.msg = await channel.send(message)
        await self.msg.add_reaction(reaction1)
        await self.msg.add_reaction(reaction2)
        await inter.response.send_message("Reaction role created!")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if self.msg.id == payload.message_id:
            print("correct message")



def setup(bot):
    bot.add_cog(reactionRoles(bot))