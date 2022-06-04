from disnake.ext.commands import Cog, slash_command


###         Help Module for Omega Bot Developed By Apollo[Ethan McKinnon]
###         Development Year: Version 0.0.5[2022 May]

class Help(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("help")

    @slash_command(name="help", description="Get help for Omega.")
    async def help(self, inter, command=""):
        if command == "":
            helpCommands = []
            for command in self.bot.slash_commands:
                helpCommands.append(command.name)
            helpCommands = sorted(helpCommands)
            list = '\n ◯ '.join(helpCommands)
            await inter.response.send_message(list, ephemeral=True)
        else:
            await self.specificCommandHelp(inter, command)
            return

    async def specificCommandHelp(self, inter, commandToGet):
        commandDict = {}
        for command in self.bot.slash_commands:
            commandDict[command.name] = command.description

        if commandDict.__contains__(commandToGet):
            commandDescription = commandDict[commandToGet]
            await inter.response.send_message(f"Help for {commandToGet} command: {commandDescription}", ephemeral=True)
        else:
            helpCommands = []
            for command in self.bot.slash_commands:
                helpCommands.append(command.name)
            helpCommands = sorted(helpCommands)
            list = '\n ◯ '.join(helpCommands)
            await inter.response.send_message(list, ephemeral=True)

def setup(bot):
    bot.add_cog(Help(bot))
