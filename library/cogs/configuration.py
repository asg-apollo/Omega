from disnake import TextChannel
from disnake.ext.commands import Cog, slash_command, has_permissions, CheckFailure

from library.db import db


class Configuration(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("configuration")

    @slash_command(name="set-Log-Channel", description="Setup the logs channel.")
    @has_permissions(manage_guild=True)
    async def setLogsChannel(self, inter, logs_channel: TextChannel):
        db.execute(f"UPDATE guildSettings SET logChannel = (?) WHERE GuildID = (?)", logs_channel.id, inter.guild.id)
        db.commit()
        await inter.send(f"Logs channel set to {logs_channel.mention}.")

    @slash_command(name="set-Suggestion-Channel", description="Setup the suggestions channel.")
    @has_permissions(manage_guild=True)
    async def setSuggestionChannel(self, inter, suggestion_channel: TextChannel):
        db.execute(f"UPDATE guildSettings SET suggestionChannel = (?) WHERE GuildID = (?)", suggestion_channel.id,
                   inter.guild.id)
        db.execute(f"UPDATE guildSettings SET SuggestModule = (?) WHERE GuildID = (?)", 1, inter.guild.id)
        db.commit()
        await inter.send(f"Suggestions channel set to {suggestion_channel.mention}.")

    @slash_command(name="enable-Moderation-Module", description="Enables the moderation module.")
    @has_permissions(manage_guild=True)
    async def enableModerationModule(self, inter):
        db.execute(f"UPDATE guildSettings SET moderationModule = (?) WHERE GuildID = (?)", 1, inter.guild.id)
        db.commit()
        await inter.send(f"Moderation module has been enabled.")

    @slash_command(name="disable-Moderation-Module", description="Disables the moderation module.")
    @has_permissions(manage_guild=True)
    async def disableModerationModule(self, inter):
        db.execute(f"UPDATE guildSettings SET moderationModule = (?) WHERE GuildID = (?)", 0, inter.guild.id)
        db.commit()
        await inter.send(f"Moderation module has been disabled.")

    @slash_command(name="enable-Suggestion-Module", description="Enables the suggestion module.")
    @has_permissions(manage_guild=True)
    async def enableSuggestionModule(self, inter):
        db.execute(f"UPDATE guildSettings SET moderationModule = (?) WHERE GuildID = (?)", 1, inter.guild.id)
        db.commit()
        await inter.send(f"Suggestion module has been enabled.")

    @slash_command(name="disable-Suggestion-Module", description="Disables the suggestion module.")
    @has_permissions(manage_guild=True)
    async def disableSuggestionModule(self, inter):
        db.execute(f"UPDATE guildSettings SET moderationModule = (?) WHERE GuildID = (?)", 0, inter.guild.id)
        db.commit()
        await inter.send(f"Suggestion module has been disabled.")

    @setLogsChannel.error
    async def setLogsChannel_error(self, inter, exc):
        if isinstance(exc, CheckFailure):
            await inter.send("You need the Manage Server permission to do that.")


def setup(bot):
    bot.add_cog(Configuration(bot))
