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

    @slash_command(name="suggest", description="Creates a suggestion")
    async def suggest(self, inter, suggestion: str):
        record = db.record("SELECT suggestModule FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0":
            await inter.response.send_message("The Suggest Module is disabled in this guild.")
            return
        else:
            db.execute(
                f"INSERT OR IGNORE INTO suggestions (GuildID, SubmitterID,suggestion, status) VALUES(?, ?, ?, ?)",
                inter.guild.id, inter.author.id, suggestion, "waiting")
            db.commit()
            await inter.response.send_message(f"Your suggestion has been added.")
            record = db.record("SELECT suggestionChannel FROM guildSettings WHERE GuildID =?", inter.guild.id)
            for (channel) in record:
                SuggestChannel = channel
                SuggestChannel = int(SuggestChannel)
            channel = self.bot.get_channel(SuggestChannel)
            embed = Embed(title="New Suggestion", color=disnake.Color.dark_teal(), timestamp=datetime.now())
            embed.add_field(name="Suggester: ", value=inter.author.mention)
            embed.add_field(name="Suggestion: ", value=suggestion)
            embed.add_field(name="Status: ", value="Waiting")
            await channel.send(embed=embed)

    @slash_command(name="seeAllSuggestions")
    async def seeAllSuggestions(self, inter, page_number: int):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return

        record = db.record("SELECT suggestModule FROM guildSettings WHERE GuildID =?", inter.guild.id)
        i = 0
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0":
            await inter.response.send_message("The Suggest Module is disabled in this guild.")
            return
        else:
            embed = Embed(title=f"Suggestions in {inter.guild.name}")
            record = db.records("SELECT * FROM suggestions WHERE (GuildID) = (?)", inter.guild.id)
            for (rowNumber ,suggestNumber, GuildID, SubmitterID, suggestion, status) in record:
                i = i + 1
                db.execute("UPDATE suggestions SET suggestNumber = (?) WHERE (rowNumber, GuildID) = (?, ?)", i, rowNumber, inter.guild.id)
                mem = inter.guild.get_member(SubmitterID)
                if page_number == 1:
                    if i <= 10:
                        embed.add_field(name=i, value=f"Name: {mem.name},\n Suggestion: {suggestion}, \n Status: {status}")
                if page_number == 2:
                    if i > 10:
                        embed.clear_fields()
                        embed.add_field(name=i,
                                        value=f"Name: {mem.name},\n Suggestion: {suggestion}, \n Status: {status}")

                db.commit()
            await inter.response.send_message(embed=embed)

    @slash_command(name="updateStatus")
    async def updateStatus(self, inter, suggestion_number, new_status):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return

        record = db.record("SELECT suggestModule FROM guildSettings WHERE GuildID =?", inter.guild.id)
        i = 0
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0":
            await inter.response.send_message("The Suggest Module is disabled in this guild.")
            return
        else:
            embed = Embed(title="Status Updated")
            memberRecord = db.record("SELECT SubmitterID FROM suggestions WHERE (GuildID, suggestNumber) = (?,?)", inter.guild.id, suggestion_number)
            statusRecord = db.record("SELECT status FROM suggestions WHERE (GuildID, suggestNumber) = (?,?)", inter.guild.id, suggestion_number)
            for (SubmitterID) in memberRecord:
                memberID = SubmitterID
            for (status) in statusRecord:
                suggestionStatus = status
            db.execute("UPDATE suggestions SET status = (?) WHERE (rowNumber, GuildID) = (?,?)", new_status, suggestion_number, inter.guild.id)

            mem = inter.guild.get_member(memberID)
            embed.add_field(name=suggestion_number, value=f"{mem.name}'s suggestion has been updated. Changes: Status is now {new_status} (Was: {status})")
            await inter.response.send_message(embed=embed)

    @slash_command(name="closeSuggestion")
    async def closeSuggestion(self, inter, suggestion_number):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return
        db.execute("DELETE FROM suggestions WHERE (suggestNumber, GuildID) = (?,?)", suggestion_number, inter.guild.id)
        db.commit()
        await inter.response.send_message(f"Suggestion {suggestion_number} has been deleted.")





def setup(bot):
    bot.add_cog(Suggestions(bot))
