from datetime import datetime
from lib2to3.pgen2.token import NAME
from os import times

import disnake
from disnake import ChannelType, TextChannel, Role, Embed, Interaction, Member
from disnake.ext.commands import command, Cog, has_permissions, CheckFailure, slash_command

from ..db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    # OLD FUNCTIONALITY (0.0.5)
    # @slash_command(name="prefix", description="Change the bots prefix.")
    # @has_permissions(manage_guild=True)
    # async def change_prefix(self, inter, new: str):
    #     if len(new) > 5:
    #         await inter.send("The prefix can not be more than 5 characters in length.")
    #     else:
    #         db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, inter.guild.id)
    #         await inter.send(f"Prefix set to {new}.")
    #
    # @change_prefix.error
    # async def change_prefix_error(self, inter, exc):
    #     if isinstance(exc, CheckFailure):
    #         await inter.send("You need the Manage Server permission to do that.")

    @slash_command(name="bot-stats", description="Stats about the bot!")
    async def botStats(self, inter):
        guildCount = 0
        commandCount = 0
        for guild in self.bot.guilds:
            guildCount += 1
        for commandInBot in self.bot.global_slash_commands:
            commandCount += 1

        embed = Embed(title="__Bot Stats__", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        embed.add_field(name="Bot Name: ", value=f"{self.bot.user.name}#{self.bot.user.discriminator}")
        embed.add_field(name="Server Count: ", value=guildCount, inline=False)
        embed.add_field(name="Command Count: ", value=commandCount, inline=False)
        embed.set_thumbnail(self.bot.user.display_avatar)
        await inter.response.send_message(embed=embed)

    @slash_command(name="guild-information", description="Get information about the guild.")
    async def guildInfo(self, inter):
        botCount = 0
        memberCount = 0
        humanCount = 0
        roleCount = 0
        categoryCount = 0
        textChannelCount = 0
        voiceChannelCount = 0
        for member in inter.guild.members:
            memberCount += 1
            if member.bot is True:
                botCount += 1
            else:
                humanCount += 1
        for role in inter.guild.roles:
            roleCount += 1

        for channel in inter.guild.channels:
            if channel.type == ChannelType.category:
                categoryCount += 1
            elif channel.type == ChannelType.text:
                textChannelCount += 1
            elif channel.type == ChannelType.voice:
                voiceChannelCount += 1
            else:
                pass

        creationDateRaw = inter.guild.created_at.date()
        creationDateRaw = str(creationDateRaw).replace("-", "/")
        creationDate = creationDateRaw

        embed = Embed(title=f"Guild Information({inter.guild.name})", color=disnake.Color.dark_teal())
        embed.set_thumbnail(inter.guild.icon)
        embed.set_footer(text=f"Guild ID: {inter.guild.id}  Guild Owner: {inter.guild.owner}")
        embed.add_field(name="Members: ", value=f"{memberCount} members, \n {humanCount} humans, \n {botCount} bots")
        embed.add_field(name="Amount of Roles: ", value=roleCount)
        embed.add_field(name="Total Channels: ",
                        value=f"{categoryCount} categories, \n {textChannelCount} text channels, \n {voiceChannelCount} voice channels")
        embed.add_field(name="Creation Date: ", value=creationDate)
        await inter.response.send_message(embed=embed)

    @slash_command(name="role-information", description="Get information about a role.")
    async def roleInformation(self, inter, role: Role):
        memberWithRole = 0
        mentionableString = ""
        displayedSeparately = ""
        roleColor = ""
        for member in role.members:
            memberWithRole += 1
        if role.mentionable is True:
            mentionableString = "Yes"
        else:
            mentionableString = "No"
        if role.hoist is True:
            displayedSeparately = "Yes"
        else:
            displayedSeparately = "No"

        if role.color is None:
            roleColor = "None"
        else:
            roleColor = role.color

        embed = Embed(title=f"Information for {role} role", color=disnake.Color.dark_teal())
        embed.set_footer(text=f"Requested By: {inter.author}    Role ID: {role.id}")
        embed.add_field(name="Role Name: ", value=role.name)
        embed.add_field(name="Mentionable: ", value=mentionableString)
        embed.add_field(name="Displayed Separately: ", value=displayedSeparately)
        embed.add_field(name="Members With Role: ", value=memberWithRole)
        embed.add_field(name="Role Color: ", value=roleColor)
        await inter.response.send_message(embed=embed)

    @slash_command(name="user-information", description="Get information about a user.")
    async def userInformation(self, inter, user: Member):
        accountCreationDate = str(user.created_at.date()).replace("-", "/")
        accountCreationTime = user.created_at.time().replace(microsecond=0)
        userJoinDate = str(user.joined_at.date()).replace("-", "/")
        userJoinTime = user.joined_at.time().replace(microsecond=0)

        roleCount = 0
        roleList = []
        if user.created_at.hour > 12:
            creationTimeDecider = "PM"
        else:
            creationTimeDecider = "AM"
        if user.joined_at.hour > 12:
            joinTimeDecider = "PM"
        else:
            joinTimeDecider = "AM"

        for role in user.roles:
            roleCount += 1
            roleList.append(role.name)

        embed = Embed(title=f"Information about {user}", color=disnake.Color.dark_teal())
        embed.set_footer(text=f"Member ID: {user.id}    Information Requested By: {inter.author}")
        embed.set_thumbnail(user.avatar)
        embed.add_field("Nickname: ", value=user.display_name)
        embed.add_field("Role Count: ", value=roleCount)
        embed.add_field("Roles: ", value=roleList)
        embed.add_field("Created Account: ", value=f"{accountCreationDate} \n {accountCreationTime} {creationTimeDecider}")
        embed.add_field("Joined Guild: ", value=f"{userJoinDate} \n {userJoinTime} {joinTimeDecider}")
        await inter.response.send_message(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))
