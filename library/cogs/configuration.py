import disnake
from click import option
from disnake import Role, TextChannel, Embed
from disnake.ext.commands import Cog, slash_command, has_permissions, CheckFailure, option_enum
from library.db import db


###         Configuration Module for Omega Bot Developed By Apollo[Ethan McKinnon]
###         Development Year: Version 0.0.5[2022 May]


class Configuration(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("configuration")

    # Create an enumerator of modules for options in the enable and disable commands.
    Modules = option_enum({"Moderation": "moderationModule", "Suggestions": "suggestionsModule",
                           "Welcome": "welcomeModule", "AutoModeration": "automodModule",
                           "Economy": "economyModule", "Fun": "funModule", "Logs": "logsModule",
                           "Random": "randomModule"})

    ModulesWithChannels = option_enum({"Logging": "logChannel", "Welcome": "welcomeChannel",
                                       "Suggestions": "suggestionChannel"})

    RoleConfigurations = option_enum({"Moderator Role": "modRole", "Restricted Role": "restrictedRole"})

    loggingOptions = option_enum({"Log Messages": "logMessages", "Log Guild Changes": "logGuildChanges", "Log User Updates": "logUserUpdates",
                                  "Log Member on Leave": "logMemberLeave", "Log Moderation Actions": "logModerationActions"})
    moderationOptions = option_enum({"DM User on Kick or Ban": "dmUserOnKickOrBan", "DM User on Moderation Action": "dmUserOnModerationAction"})
    autoModerationOptions = option_enum({"Delete All Links": "deleteAllLinks", "Delete Blacklisted Links": "deleteBlacklistedLinks", "Delete Blacklisted Words": "deleteBlacklistedWords"})

    enableOrDisableOption = option_enum({"Enable": "enable", "Disable": "disable"})

    # Enable a module within the guild. Has a list of options(All modules in the bot).
    @slash_command(name="toggle-module")
    async def toggleModule(self, inter, toggle: enableOrDisableOption, modules: Modules):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Grabs the lowest moderator role from the database
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)  # Get the role object

        if inter.author.top_role < modRole:  # Checks if the authors highest role is lower than the moderation role, if not, send a error message:
            if inter.author != inter.guild.owner:
                await inter.response.send_message("You do not have permission to use this command.")
                return
            else:
                pass

        record = db.record(f"SELECT {modules} FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if toggle == "enable":
            if moduleStatus == 1:
                await inter.response.send_message(f"{modules} is already enabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guildSettings SET {modules} = (?) WHERE GuildID = (?)", 1, inter.guild.id)  # Update the guild settings and change the module to enabled.
                if modules == "moderationModule":
                    await inter.response.send_message(f"{modules} has been enabled. **WARNING** You must use the /set-role command for these commands to work!")
                elif modules == "logsModule":
                    await inter.response.send_message(f"{modules} has been enabled. **WARNING** You must use the /set-channel command for logging to work!")
                elif modules == "suggestionsModule":
                    await inter.response.send_message(f"{modules} has been enabled. **WARNING** You must use the /set-channel and /set-role(Not needed if previously set) command for these commands "
                                                      f"to work!")
                elif modules == "economyModule":
                    await inter.response.send_message(f"{modules} has been enabled. **WARNING** You must use the /set-role command for these commands to work!")
                else:
                    await inter.response.send_message(f"{modules} has been enabled.")
        if toggle == "disable":
            if moduleStatus == 0:
                await inter.response.send_message(f"{modules} is already disabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guildSettings SET {modules} = (?) WHERE GuildID = (?)", 0, inter.guild.id)  # Update the guild settings and change the module to enabled.
                await inter.response.send_message(f"{modules} has been disabled.")

        db.commit()

    @slash_command(name="set-channel")
    async def setChannel(self, inter, modules: ModulesWithChannels, channel: TextChannel):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Grabs the lowest moderator role from the database
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)  # Get the role object

        if inter.author.top_role < modRole:  # Checks if the authors highest role is lower than the moderation role, if not, send a error message:
            if inter.author != inter.guild.owner:
                await inter.response.send_message("You do not have permission to use this command.")
                return
            else:
                pass

        db.execute(f"UPDATE guildSettings SET {modules} = (?) WHERE GuildID = (?)", channel.id, inter.guild.id)
        db.commit()

        if modules == "logChannel":
            channelName = "Logs"
        elif modules == "welcomeChannel":
            channelName = "Welcome"
        elif modules == "suggestionChannel":
            channelName = "Suggestions"
        else:
            return

        await inter.response.send_message(f"{channelName} channel has been set to {channel.mention}.")

    @slash_command(name="set-role", scope=889946079188095006)
    async def setRole(self, inter, role_options: RoleConfigurations, role: Role):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Grabs the lowest moderator role from the database
        for (modRole) in record:
            modRole = modRole

        modRole = inter.guild.get_role(modRole)  # Get the role object
        if inter.author != inter.guild.owner:
            if inter.author.top_role < modRole:  # Checks if the authors highest role is lower than the moderation role, if not, send a error message:
                await inter.response.send_message("You do not have permission to use this command.")
                return

        db.execute(f"UPDATE guildSettings SET {role_options} = (?) WHERE GuildID = (?)", role.id, inter.guild.id)
        db.commit()

        if role_options == "modRole":
            RoleName = "Minimum moderator"
        elif role_options == "restrictedRole":
            RoleName = "Restricted"

        await inter.response.send_message(f"{RoleName} role has been set to {role.name}.")

    @slash_command(name="config-module", description="Configure a module.")
    async def configModule(self, inter):
        pass

    @configModule.sub_command()
    async def Moderation(self, inter, toggle: enableOrDisableOption, setting: moderationOptions):
        record = db.record(f"SELECT {setting} FROM guilds WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            settingStatus = rec

        if toggle == "enable":
            if settingStatus == 1:
                await inter.response.send_message(f"{setting} is already enabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guilds SET {setting} = (?) WHERE GuildID = (?)", 1, inter.guild.id)
                await inter.response.send_message(f"{setting} has been enabled.")
        elif toggle == "disable":
            if settingStatus == 0:
                await inter.response.send_message(f"{setting} is already disabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guilds SET {setting} = (?) WHERE GuildID = (?)", 0, inter.guild.id)
                await inter.response.send_message(f"{setting} has been disabled.")
        db.commit()

    @configModule.sub_command()
    async def Logging(self, inter, toggle: enableOrDisableOption, setting: loggingOptions):
        record = db.record(f"SELECT {setting} FROM guilds WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            settingStatus = rec

        if toggle == "enable":
            if settingStatus == 1:
                await inter.response.send_message(f"{setting} is already enabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guilds SET {setting} = (?) WHERE GuildID = (?)", 1, inter.guild.id)
                await inter.response.send_message(f"{setting} has been enabled.")
        elif toggle == "disable":
            if settingStatus == 0:
                await inter.response.send_message(f"{setting} is already disabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guilds SET {setting} = (?) WHERE GuildID = (?)", 0, inter.guild.id)
                await inter.response.send_message(f"{setting} has been disabled.")
        db.commit()

    @configModule.sub_command()
    async def AutoModeration(self, inter, toggle: enableOrDisableOption, setting: autoModerationOptions):
        record = db.record(f"SELECT {setting} FROM guilds WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            settingStatus = rec

        if toggle == "enable":
            if settingStatus == 1:
                await inter.response.send_message(f"{setting} is already enabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guilds SET {setting} = (?) WHERE GuildID = (?)", 1, inter.guild.id)
                await inter.response.send_message(f"{setting} has been enabled.")
        elif toggle == "disable":
            if settingStatus == 0:
                await inter.response.send_message(f"{setting} is already disabled in this guild.")
                return
            else:
                db.execute(f"UPDATE guilds SET {setting} = (?) WHERE GuildID = (?)", 0, inter.guild.id)
                await inter.response.send_message(f"{setting} has been disabled.")
        db.commit()

    # @slash_command(name="view-all-modules")
    # async def viewAllModules(self, inter):
    #     i = 0
    #     embed = Embed(title="All Modules", color=disnake.Color.dark_teal())
    #     record = db.records("SELECT suggestionsModule, moderationModule, welcomeModule, automodModule, economyModule, funModule, logsModule, miscModule, randomModule FROM guildSettings WHERE "
    #                         "GuildID = (?)", inter.guild.id)
    #     moduleList = ["Suggestions", "Moderation", "Welcome", "AutoMod", "Economy", "Fun", "Logs", "Misc", "Random"]
    #     for module in record:
    #
    #         moduleStatusList = []
    #         moduleSplit = str(module).split(", ")
    #         for num in moduleSplit:
    #             moduleStatusList.append(num)
    #         i += 1
    #         if moduleStatusList[i] == "1":
    #             embed.add_field(name=moduleList[i], value="Enabled")
    #         elif moduleStatusList[i] == "0":
    #             embed.add_field(name=moduleList[i], value="Disabled")
    #     await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Configuration(bot))
