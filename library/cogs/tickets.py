import asyncio

import disnake
from disnake.ext.commands import Cog, slash_command

###         Ticketing Module for Omega Bot Developed By Apollo[Ethan McKinnon]
###         Development Year: Version 0.0.5[2022 May]
from library.db import db


class tickets(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("tickets")

            ### MEMBER COMMMANDS [START]

    @slash_command(name="open-ticket")
    async def openTicket(self, inter):
        record = db.record("SELECT ticketModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            ticketModuleStatus = rec
        if ticketModuleStatus == 0:  # If the ticket module is disabled, send an error and return
            await inter.response.send_message("Ticket module is disabled.")
            return

        record = db.record("SELECT channelID FROM tickets WHERE (GuildID, UserID) = (?,?)", inter.guild.id, inter.author.id)
        if record is not None:
            for rec in record:
                await inter.response.send_message("You already have a ticket open.")
        else:

            record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
            for (role) in record:
                modRole = role
                modRole = int(modRole)

            overwrites = {
                inter.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                inter.guild.me: disnake.PermissionOverwrite(view_channel=True),
                inter.guild.get_role(modRole): disnake.PermissionOverwrite(view_channel=True)
            }

            ticketChannel = await inter.guild.create_text_channel(f"{inter.author.name}'s Ticket", reason="Opening a ticket", overwrites=overwrites)
            ticketChannelID = ticketChannel.id
            db.execute("INSERT OR IGNORE INTO tickets (GuildID, UserID, ChannelID) VALUES(?,?,?)", inter.guild.id, inter.author.id, ticketChannelID)
            db.commit()
            await inter.response.send_message(f"Your ticket has been opened.", delete_after=15)
            await ticketChannel.send(f"{inter.author.mention} this is your ticket. Please place your question here and a staff member will reach out to you shortly.")

    @slash_command(name="close-ticket")
    async def closeTicket(self, inter):
        record = db.record("SELECT ticketModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            ticketModuleStatus = rec
        if ticketModuleStatus == 0:  # If the ticket module is disabled, send an error and return
            await inter.response.send_message("Ticket module is disabled.")
            return

        record = db.record("SELECT channelID FROM tickets WHERE (GuildID, UserID) = (?,?)", inter.guild.id, inter.author.id)
        if record is None:
            await inter.response.send_message(f"You do not currently have a ticket open.")
        for rec in record:
            ticketChannelID = rec

        ticketChannel = inter.guild.get_channel(ticketChannelID)
        if inter.channel.id != ticketChannelID:
            await inter.response.send_message(f"Tickets can only be closed from within the tickets channel. Your tickets channel is {ticketChannel.mention}.")
        elif inter.channel.id == ticketChannelID:
            db.execute("DELETE FROM tickets WHERE (GuildID, UserID, channelID) = (?,?,?)", inter.guild.id, inter.author.id, ticketChannelID)
            await inter.response.send_message("Ticket closing... This channel will be deleted in 60 seconds")
            await asyncio.sleep(60)
            await inter.channel.delete(reason="Ticket Closing")

            ### MEMBER COMMANDS [END]

            ### ADMIN COMMANDS [START]

    @slash_command(name="force-close-ticket")
    async def forceCloseTicket(self, inter):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if inter.author.top_role < modRole:  # If the authors highest role in the guild hierarchy is lower than the moderator role, fail and return a message
            await inter.response.send_message("You do not have permission to use this command.")
            return

        record = db.record("SELECT ticketModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            ticketModuleStatus = rec
        if ticketModuleStatus == 0:  # If the ticket module is disabled, send an error and return
            await inter.response.send_message("Ticket module is disabled.")
            return

        record = db.records("SELECT GuildID, UserID, channelID FROM tickets WHERE (GuildID) = (?)", inter.guild.id)
        if record is None:
            await inter.response.send_message("This is not a ticket channel.")
        for (GuildID, UserID, channelID) in record:
            ticketChannelID = channelID
            if inter.channel.id != ticketChannelID:
                pass
            else:
                ticketChannel = inter.guild.get_channel(ticketChannelID)
                await inter.response.send_message("Ticket closing... This channel will be deleted in 20 seconds")
                await asyncio.sleep(20)
                await ticketChannel.delete(reason="Ticket Closing")
                db.execute("DELETE FROM tickets WHERE (GuildID, UserID, channelID) = (?,?,?)", inter.guild.id, inter.author.id, ticketChannelID)
                db.commit()


def setup(bot):
    bot.add_cog(tickets(bot))
