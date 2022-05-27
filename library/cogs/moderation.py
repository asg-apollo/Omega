import asyncio
from datetime import datetime

import disnake
from disnake import Member, Embed, Role
from disnake.ext.commands import Cog, has_permissions, slash_command, MissingRole, MissingPermissions

from library.cogs import logs
from Development import configuration
from library.db import db


class Moderation(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.modRole = ''

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("moderation")

    ###     Punishment Commands[START]


    # Bans the mentioned member with an optional reason. Requires the ban_members permission.
    @has_permissions(ban_members=True)
    @slash_command(name="ban", description="[MODERATION] Bans the mentioned member.")
    async def _ban(self, inter, member: Member, *, reason=''):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        await logs.Logs.log_ban(self, member, reason, configuration.leaveLogsChannel, inter) # Log the ban to the dedicated logs channel.
        await member.ban(reason=reason) # Ban the member with the select reason.
        await inter.send(f"{member} Banned.")

    # Kicks the mentioned member with an optional reason. Requires the kick_members permission.
    @has_permissions(kick_members=True)
    @slash_command(name="kick", description="[MODERATION] Kicks the mentioned member.")
    async def _kick(self, inter, member: Member, *, reason=''):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        await logs.Logs.log_kick(self, member, reason, configuration.leaveLogsChannel, inter) # Log the kick to the designated logs channel.
        await member.kick(reason=reason) # Kick the member with the given reason.
        await inter.send(f"{member} kicked.")

    # Restrict a member with an optional amount of time. Requires the kick_members permission.
    @has_permissions(kick_members=True)
    @slash_command(name="restrict",
                    description="[MODERATION] Restricts the mentioned member, removing the ability to message for x amount of "
                    "seconds.")
    async def _restricted(self, inter, member: Member, *, duration: int):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": #If the moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        db.execute("INSERT OR IGNORE INTO restricted (UserID) VALUES(?)", member.id) # Insert the member into the restricted table in the database
        db.execute(f"UPDATE restricted SET durationTillUnrestricted = (?) WHERE UserID = (?)", duration, member.id) # Update the restricted table with the duration where the members id is.
        db.commit()

        if duration is None: # If duration was not provided, default to 60s
            duration = 60

        record = db.record("SELECT restrictedRole FROM guildSettings WHERE GuildID =?", inter.guild.id) # Grabs the restricted role from the database
        for (configRole) in record:
            restrictedRole = configRole

        role = disnake.utils.get(inter.guild.roles, name=restrictedRole) # Gets the role by name

        await logs.Logs.log_restrict(self, member, duration, configuration.moderationLogsChannel, inter) # Logs the restriction to the designated logs channel.
        await inter.response.send_message(f"{member.mention} has been restricted for {duration}s.") 
        await member.add_roles(role) # Add the restricted role to the member
        await asyncio.sleep(duration) # Wait until restriction is up
        await member.remove_roles(role) # Remove the restricted role from the member
        duration = 0 # Set duration back to 0
        reason = "Automatic Restriction Lifted" # Provide a reason for the unrestrict
        await logs.Logs.log_unrestrict(self, member, reason, configuration.moderationLogsChannel, inter) # Log the unrestriction


    ### PUNISHMENT COMMANDS[ENDS]


    ### PUNISHMENT LIFTING COMMANDS[START]

    # Unbans the member with the provided id with an optional reason. Requires the ban_members permission.
    @has_permissions(ban_members=True)
    @slash_command(name="unban", description="[MODERATION] Unbans the chosen user ID.")
    async def _unban(self, inter, memberID: int, *, reason=''):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If moderation module is disabled, send an error and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        member = await self.bot.fetch_user(memberID) # Fetch the user object by ID
        banned_users = await self.bot.guild.bans() # Grabs the guilds ban list
        for ban_entry in banned_users: # Checks if the user id is in the ban list.
            user = ban_entry.user
            if user.id == member.id: # If members id is in the ban list, continue
                await inter.guild.unban(user) # Unban the member
                await logs.Logs.log_unban(self, memberID, reason, configuration.leaveLogsChannel, inter) # Log the unban in the designated logs channel.
                await inter.send(f"{member.display_name} has been unbanned.")
                return

    # Unrestrict the mentioned member with an optional reason. Requires the kick_members permission.
    @has_permissions(kick_members=True)
    @slash_command(name="unrestrict", description="[MODERATION] Unrestricts the mentioned member.")
    async def _unrestrict(self, inter, member: Member, *, reason=''):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        record = db.record("SELECT restrictedRole FROM guildRoles WHERE GuildID =?", inter.guild.id) # Grab the guilds restricted role from the database
        for (configRole) in record:
            restrictedRole = configRole

        role = disnake.utils.get(inter.guild.roles, name=restrictedRole) # Gets the role object
        if role in member.roles: # If the role is in the members roles, continue
            await inter.send(f"{member.mention} has been unrestricted.")
            await member.remove_roles(role) # Removes the restricted role from the member.
            await logs.Logs.log_unrestrict(self, member, reason, configuration.moderationLogsChannel, inter) # Log the unrestriction to the designated logs channel
        else:
            await inter.send(f"{member} is not restricted!")

    # Clears the specified amount of messages. Requires the manage_messages permission. Cannot delete messages over 14 days.
    @has_permissions(manage_messages=True)
    @slash_command(name="clear", description="[MODERATION] Deletes the inputted amount of messages in a channel.")
    async def _clear(self, inter, amount: int):
        await inter.response.defer()
        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record: 
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the moderation module is disabled, send a error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return
        mgs = [] # Create a empty list of messages
        async for x in inter.channel.history(limit=amount):
            mgs.append(x)

        await inter.channel.delete_messages(mgs) # Delete the list of messages
        await inter.channel.send(f"{amount} messages have been deleted in {inter.channel.mention}!", delete_after=5)

    # Gives roles with the provided user ID. Requires the moderate_members permission.
    @has_permissions(moderate_members=True)
    @slash_command(name="give_role_via_id", description="[MODERATION] Gives the role with the inputted id to the user.")
    async def give_role_with_id(self, inter, member: Member, role_id=0):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        role_id = int(role_id) # Ensure the role_id is an integer
        role = inter.guild.get_role(role_id) # Get the role object

        roleList = [] # Create an empty list of roles
        for storedRoles in member.roles:
            roleList.append(storedRoles.name) # Append each of the members roles to the list

        if role in member.roles: # Check if the role is in the members roles already
            await inter.response.send_message(f"{member.mention} already has that role.")
            return
        elif role_id != 0:

            await member.add_roles(role) # Add the role to the member
            await inter.response.send_message(f"{role} has been added to {member.mention}.")

            # Create and send an embed with the roles that have been changed.
            embed = Embed(title=f"*{role}* Given To {member}", color=disnake.Color.dark_teal(), timestamp=datetime.now())
            embed.add_field(name="Roles Before: ", value=roleList)
            await inter.channel.send(embed=embed)
            # TODO Add Logging to this command

    # Gives a role to the mentioned member. Requires the moderate_members permission.
    @has_permissions(moderate_members=True)
    @slash_command(name="give_role_via_mention", description="[MODERATION] Gives the role with the mentioned role to the user.")
    async def give_role_with_mention(self, inter, member: Member, role: Role):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the moderation module is disabled, send an error message and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        roleList = [] # Create an empty list of roles
        for storedRoles in member.roles:
            roleList.append(storedRoles.name) # Append each of the members roles to the list

        if role in member.roles: # If the role is already in the member's roles, send an error and return.
            await inter.response.send_message(f"{member.mention} already has that role.")
            return
        elif role is not None:
            await member.add_roles(role) # Add the role to the member
            await inter.response.send_message(f"{role} has been added to {member.mention}.")

            # Create and send an embed with the roles that have been changed.
            embed = Embed(title=f"*{role}* Given To {member}", color=disnake.Color.dark_teal(), timestamp=datetime.now())
            embed.add_field(name="Roles Before: ", value=roleList)
            await inter.channel.send(embed=embed)
            # TODO Add Logging to the command

    # Remove a role via ID from a member. Requires the moderate_members permission.
    @has_permissions(moderate_members=True)
    @slash_command(name="remove_role_via_id", description="Removes the role with the inputted id from the user.")
    async def remove_role_with_id(self, inter, member: Member, role_id=0):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the moderation module is disabled, send an error and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        roleList = [] # Create an empty list of roles
        for storedRoles in member.roles:
            roleList.append(storedRoles.name) # Append the member's roles to the list

        role_id = int(role_id) # Ensure that the ID is an integer
        role = inter.guild.get_role(role_id) # Get the role object

        if role not in member.roles: # If role is not in member's roles, send an error and return.
            await inter.response.send_message(f"{member.mention} doesn't have that role.")
            return
        elif role_id != 0:
            await member.remove_roles(role) # Remove the role from the member.
            await inter.response.send_message(f"{role} has been removed from {member.mention}.")

            # Create and send an embed with the roles that have been changed.
            embed = Embed(title=f"*{role}* Removed From {member}", color=disnake.Color.red(), timestamp=datetime.now())
            embed.add_field(name="Roles Before Removal: ", value=roleList)
            await inter.channel.send(embed=embed)
            # TODO Add logging to the command

    # Remove a role via mentioning the role. Requires the moderate_members permission.
    @has_permissions(moderate_members=True)
    @slash_command(name="remove_role_via_mention",
                    description="[MODERATION] Removes the role with the mentioned role from the user.")
    async def remove_role_with_mention(self, inter, member: Member, role: Role):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)

        if isFalse == "0": # If moderation module is disabled, send an error and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        if role not in member.roles: # If the role is not in the member's roles, send an error and return.
            await inter.response.send_message(f"{member.mention} doesn't have that role.")
            return
        elif role is not None:
            roleList = [] # Create an empty role list.
            for storedRoles in member.roles:
                roleList.append(storedRoles.name) # Append the member's roles to the list.

            await member.remove_roles(role) # Remove the role from the member.
            await inter.response.send_message(f"{role} has been removed from {member.mention}.")

            # Create and send an embed with the roles that have been changed.
            embed = Embed(title=f"*{role}* Removed From {member}", color=disnake.Color.red(), timestamp=datetime.now())
            embed.add_field(name="Roles Before Removal: ", value=roleList)
            await inter.channel.send(embed=embed)
            # TODO Add logging to the command

    # Remove all roles from a member. Requires the moderate_members permission.
    @has_permissions(moderate_members=True)
    @slash_command(name="remove_all_roles",
                    description="Removes all roles from the user.")
    async def remove_all_roles(self, inter, member: Member):

        record = db.record("SELECT moderationModule FROM guildSettings WHERE GuildID =?", inter.guild.id) # Check the database to see if the moderation module is enabled in the guild.
        for (configBool) in record:
            isFalse = configBool
            int(isFalse)
        if isFalse == "0": # If the moderatation module is disabled, send an error and return.
            await inter.response.send_message("The Moderation Module is disabled in this guild.")
            return

        roleList = [] # Create an empty role list
        for storedRoles in member.roles:
            roleList.append(storedRoles.name) # Append the member's roles to the list.

        if member.roles == 1: # If the member only has the @everyone role, send an error and return.
            await inter.response.send_message(f"{member.mention} doesn't have any roles.")
            return

        for role in member.roles: # For each role in the member's roles, try to remove the role.
            try:
                await member.remove_roles(role)
            except:
                print(f"Can't remove the role {role}")

        await inter.response.send_message(f"All roles have been removed from {member.mention}.")

        # Create and send an embed with all roles that have been changed.
        embed = Embed(title=f"*All roles* Removed From {member}", color=disnake.Color.red(), timestamp=datetime.now())
        embed.add_field(name="Roles Before Removal: ", value=roleList)
        await inter.channel.send(embed=embed)
        #TODO Add logging to the command
    

    ### PUNISHMENT LIFTING COMMANDS[END]

    ### ERROR HANDLING[STARTS]
    
    @_ban.error
    async def _ban_error(self, inter, exc):
        if isinstance(exc, MissingPermissions):
            await inter.response.send_message("You are missing the Ban Members Permission.")

    @_clear.error
    async def _clear_error(self, inter, exc):
        print(exc)

    @give_role_with_mention.error
    async def give_role_with_mention_error(self, inter, exc):
        if isinstance(exc, MissingRole):
            await inter.response.send_message("You are missing the required role.")

    @give_role_with_id.error
    async def give_role_with_id_error(self, inter, exc):
        if isinstance(exc, MissingRole):
            await inter.response.send_message("You are missing the required role.")

    ### ERROR HANDLING[ENDS]


    ### YET TO BE ADDED
    """ VERSION: 0.5.0 

    @slash_command(name="mass-change-nicknames", scope=889946079188095006)
    async def massChangeNicknames(self, inter, wordToChange: str, wordToChangeTo=""):
        if wordToChangeTo is None:
            wordToChangeTo = ""
            selectedStringToReplaceVal = "No string specified, replaced with nothing."
    
        memberNickname = ""
        amountOfUsersUpdated = 0
    
        for member in inter.guild.members:
            memberNickname = member.display_name
            if wordToChange in memberNickname:
                memberNickname = memberNickname.replace(wordToChange, wordToChangeTo)
                await member.edit(nick=memberNickname)
                amountOfUsersUpdated += 1
    
        emb = Embed(title=f"Nickname Changer", color=disnake.Color.dark_teal())
        emb.add_field(name="Amount of users updated:", value=amountOfUsersUpdated, inline=False)
        emb.add_field(name="Selected String to be removed:", value=wordToChange, inline=False)
        emb.add_field(name="Selected String to Replace:", value=selectedStringToReplaceVal, inline=False)
        await inter.response.send_message(embed=emb)
    """


def setup(bot):
    bot.add_cog(Moderation(bot))
