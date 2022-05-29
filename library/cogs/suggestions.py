from datetime import datetime

import disnake
from disnake import Embed, Member
from disnake.ext.commands import Cog, slash_command
from ..db import db


class Suggestions(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("suggestions")

    ###         @EVERYONE COMMANDS[START]

    @slash_command(name="suggest", description="Creates a suggestion")
    async def suggest(self, inter, suggestion: str):
        record = db.record("SELECT suggestionsModule FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Check the database to see if the suggestModule is enabled.
        for (configBool) in record:
            isFalse = configBool
        if isFalse == 0:  # If the suggestion module is disabled, send an error and return
            await inter.response.send_message("The Suggestion Module is disabled in this guild.")
            return
        else:
            record = db.record("SELECT suggestionChannel FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Selects the suggestionsChannel from the database.
            for (channel) in record:
                if channel is None:
                    await inter.response.send_message("No suggestion channel has been setup yet. Please get an administrator to set a suggestion channel with /set-channel.")
                SuggestChannel = channel
                SuggestChannel = int(SuggestChannel)
            channel = self.bot.get_channel(SuggestChannel)

            # Create and send an embed with the information about the suggestion to the suggestions channel.
            embed = Embed(title="New Suggestion", color=disnake.Color.dark_teal(), timestamp=datetime.now())
            embed.add_field(name="Suggester: ", value=inter.author.mention)
            embed.add_field(name="Suggestion: ", value=suggestion)
            embed.add_field(name="Status: ", value="Waiting")
            await inter.response.send_message(f"Your suggestion has been added.")
            await channel.send(embed=embed)

            db.execute(
                f"INSERT OR IGNORE INTO suggestions (GuildID, SubmitterID,suggestion, status) VALUES(?, ?, ?, ?)",
                inter.guild.id, inter.author.id, suggestion, "waiting")  # Insert a suggestion record into the database
            db.commit()

    ###         @EVERYONE COMMANDS[END]

    ###         ADMIN COMMANDS[START]

    # Get all the suggestions and view them.
    @slash_command(name="seeAllSuggestions")
    async def seeAllSuggestions(self, inter, page_number: int):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id) # Get the minimum moderator role from the database
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if inter.author.top_role < modRole:  # If the authors highest role in the guild hierarchy is lower than the moderator role, fail and return a message
            await inter.response.send_message("You do not have permission to use this command.")
            return

        record = db.record("SELECT suggestionsModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see whether the suggestModule is enabled or not
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the suggestModule is disabled, send an error and return
            await inter.response.send_message("The Suggestion Module is disabled in this guild.")
            return
        else:
            i = 0
            embed = Embed(title=f"Suggestions in {inter.guild.name}", color=disnake.Color.dark_teal(), timestamp=datetime.utcnow()) # Create an embed storing all of the suggestions
            record = db.records("SELECT * FROM suggestions WHERE (GuildID) = (?)", inter.guild.id) # Select all of the suggestions from the database
            for (rowNumber, suggestNumber, GuildID, SubmitterID, suggestion, status) in record:
                i = i + 1
                db.execute("UPDATE suggestions SET suggestNumber = (?) WHERE (rowNumber, GuildID) = (?, ?)", i, rowNumber, inter.guild.id) # Update the suggestion to have a suggestion number
                mem = inter.guild.get_member(SubmitterID)
                if page_number == 1:
                    if i <= 10:
                        embed.add_field(name=i, value=f"Name: {mem.name},\n Suggestion: {suggestion}, \n Status: {status}")
                if page_number == 2:
                    if i > 10:
                        if i < 21:
                            embed.add_field(name=i,
                                        value=f"Name: {mem.name},\n Suggestion: {suggestion}, \n Status: {status}")
                if page_number == 3:
                    if i >= 21:
                        if i < 31:
                            embed.add_field(name=i,
                                        value=f"Name: {mem.name},\n Suggestion: {suggestion}, \n Status: {status}")
                if page_number == 4:
                    if i >= 31:
                        if i < 41:
                            embed.add_field(name=i,
                                        value=f"Name: {mem.name},\n Suggestion: {suggestion}, \n Status: {status}")
                if page_number == 5:
                    if i >= 41:
                        if i < 51:
                            embed.add_field(name=i,
                                        value=f"Name: {mem.name},\n Suggestion: {suggestion}, \n Status: {status}")
                if page_number >= 6:
                    inter.response.send_message("There is a maximum of six pages worth of suggestions.")

                db.commit()
            await inter.response.send_message(embed=embed) # Send the embed

    # Update a status | should be used after using seeAllSuggestions
    @slash_command(name="updateStatus")
    async def updateStatus(self, inter, suggestion_number, new_status):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if inter.author.top_role < modRole:  # If the authors highest role in the guild hierarchy is lower than the moderator role, fail and return a message
            await inter.response.send_message("You do not have permission to use this command.")
            return

        record = db.record("SELECT suggestionsModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the suggestionsModule is enabled
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the suggestionsModule is disabled, send an error and return
            await inter.response.send_message("The Suggestion Module is disabled in this guild.")
            return
        else:
            embed = Embed(title="Status Updated", color=disnake.Color.dark_teal(), timestamp=datetime.utcnow()) # Create an embed with details about the updated suggestion
            memberRecord = db.record("SELECT SubmitterID FROM suggestions WHERE (GuildID, suggestNumber) = (?,?)", inter.guild.id, suggestion_number) # Get the submittedID from the database
            statusRecord = db.record("SELECT status FROM suggestions WHERE (GuildID, suggestNumber) = (?,?)", inter.guild.id, suggestion_number) # Get the status from the database
            for (SubmitterID) in memberRecord:
                memberID = SubmitterID
            for (status) in statusRecord:
                suggestionStatus = status
            db.execute("UPDATE suggestions SET status = (?) WHERE (suggestNumber, GuildID) = (?,?)", new_status, suggestion_number, inter.guild.id) # Update the database with the new status
            db.commit()
            mem = inter.guild.get_member(memberID)
            embed.add_field(name=suggestion_number, value=f"{mem.name}'s suggestion has been updated. Changes: Status is now {new_status} (Was: {status})")
            await inter.response.send_message(embed=embed) # Send the embed

    # Close a suggestion | Should be used after seeAllSuggestions
    @slash_command(name="closeSuggestion")
    async def closeSuggestion(self, inter, suggestion_number):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if inter.author.top_role < modRole:  # If the authors highest role in the guild hierarchy is lower than the moderator role, fail and return a message
            await inter.response.send_message("You do not have permission to use this command.")
            return

        record = db.record("SELECT suggestionsModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the suggestionsModule is enabled
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)

        db.execute("DELETE FROM suggestions WHERE (suggestNumber, GuildID) = (?,?)", suggestion_number, inter.guild.id) # Delete the suggestion from the database
        db.commit()
        await inter.response.send_message(f"Suggestion {suggestion_number} has been deleted.")

    ###         ADMIN COMMANDS[END]


def setup(bot):
    bot.add_cog(Suggestions(bot))
