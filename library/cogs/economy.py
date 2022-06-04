import random
from datetime import datetime
import disnake
from disnake import Embed, Member, TextInput
from disnake.ext.commands import Cog, slash_command, cooldown, BucketType
import functools
import json
from library.cogs import logs
from library.db import db

"""
            Economy Module for Omega Bot Developed By Apollo[Ethan McKinnon]
            Development Year: Version 0.5.0[2022 May]
"""


async def openAccount(GuildID, UserID):  # Can be called by any command to open/see if the member has an account.
    print("Opening account")
    db.execute("INSERT OR IGNORE INTO economy (GuildID, UserID) VALUES(?,?)", GuildID, UserID)
    db.commit()


async def checkAllCoins(inter):  # Can be called from any command to see the total amount of coins within the guild.
    record = db.records("SELECT balance FROM economy WHERE (GuildID) = (?)", inter.guild.id)
    totalCoins = 0
    for (balance) in record:
        res = functools.reduce(lambda sub, ele: sub * 10 + ele, balance)
        totalCoins = totalCoins + res
    return totalCoins


class Economy(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("economy")  # Readys the Economy Module

    ### MEMBER COMMANDS [START]

        ### MONEY MAKING COMMANDS [START]
    @cooldown(1, 3600, type=BucketType.user)
    @slash_command(name="work", description="Work for one hour and make some money!")
    async def Work(self, inter):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        # Grab the balance of the member if it exists
        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, inter.author.id)
        if record is None:  # If the member does not have an account, open an account
            await openAccount(inter.guild.id, inter.author.id)
        # Grabs the balance of the member
        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, inter.author.id)

        for (balance) in balRecord:
            memberBalance = balance  # Set balance to a integer instead of a tuple

        income = random.randrange(10, 90)
        memberBalance += income
        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?,?)", memberBalance ,inter.guild.id, inter.author.id)

        await inter.response.send_message(f"You have earned {income} coins in an hour! You balance is now {memberBalance} coins!")

    @cooldown(1, 10, type=BucketType.user)
    @slash_command(name="mug", description="Mug a member!")
    async def mugMember(self, inter, target: Member):
        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0:  # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        if target.bot is True:
            await inter.response.send_message("You cannot mug a bot.")
            return

        if target.id == inter.author.id:
            await inter.response.send_message("You cannot mug yourself.")
            return

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, inter.author.id)
        if record is None:  # If the member does not have an account, open an account
            await openAccount(inter.guild.id, inter.author.id)
        # Grabs the balance of the member
        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, inter.author.id)

        for (balance) in balRecord:
            authorBalance = balance  # Set balance to a integer instead of a tuple

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, target.id)
        if record is None:  # If the member does not have an account, open an account
            await openAccount(inter.guild.id, target.id)
        # Grabs the balance of the member
        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, target.id)
        for (balance) in balRecord:
            targetBalance = balance  # Set balance to a integer instead of a tuple

        stolenAmount = random.randrange(5, 45)
        targetBalance -= stolenAmount
        authorBalance += stolenAmount

        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?,?)", targetBalance, inter.guild.id, target.id)
        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?,?)", authorBalance, inter.guild.id, inter.author.id)
        db.commit()
        await inter.response.send_message(f"{inter.author.mention} stole {stolenAmount} coins from {target.mention}!")

    # See the balance of whoever ran the command.
    @slash_command(name="balance", description="View your balance!")
    async def balance(self, inter):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        # Grab the balance of the member if it exists
        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, inter.author.id)
        if record is None:  # If the member does not have an account, open an account
            await openAccount(inter.guild.id, inter.author.id)
        # Grabs the balance of the member
        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id, inter.author.id)

        for (balance) in balRecord:
            memberBalance = balance  # Set balance to a integer instead of a tuple

        # Create and send an embed with the members balance
        em = Embed(title=f"{inter.author.name}'s balance", color=disnake.Color.dark_teal())
        em.add_field(name="Bank balance", value=memberBalance)
        em.set_thumbnail(url=inter.author.avatar)
        await inter.response.send_message(embed=em)

    # Transfer coins from the authors account to the selected members account
    @slash_command(name="transfer-coins",
                   description="Transfers the determined amount of coins to the mentioned member.")
    async def transferCoins(self, inter, member: Member, amount: int):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        if member.bot is True:
            await inter.response.send_message("You can't give coins to a bot.")
            return

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           inter.author.id)  # Grabs the balance of whoever ran the command
        if record is None:  # If the person who ran the command does not have an account, open an account
            await openAccount(inter.guild.id, inter.author.id)

        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              inter.author.id)
        for (authorBalance) in balRecord:
            authorBalance = authorBalance  # Convert authorBalance from a tuple to an integer

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           member.id)  # Grabs the balance of the selected member
        if record is None:  # If member does not have an account, open an account
            await openAccount(inter.guild.id, member.id)

        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              member.id)  # Regrabs the balance of the selected member
        for (memberBalance) in balRecord:
            memberBalance = memberBalance  # Convert memberBalance from a tuple to an integer

        amountToRemove = authorBalance - amount
        amountToGive = memberBalance + amount

        if authorBalance - amountToRemove < 0:
            await inter.response.send_message("You do not have enough coins.")
            return
        elif amount < 0:
            await inter.response.send_message("You cannot give a negative amount of coins.")
            return

        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?, ?)", amountToRemove, inter.guild.id,
                   inter.author.id)  # Updates the authors balance
        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?, ?)", amountToGive, inter.guild.id,
                   member.id)  # Updates the members balance
        db.commit()  # Commit to the database

        # Create and sends an embed with the updated balances
        embed = Embed(title="Updated Balances", color=disnake.Color.dark_teal())
        embed.add_field(name=f"{inter.author.name}'s Balance: ", value=f"{amountToRemove}")
        embed.add_field(name=f"{member.name}'s Balance: ", value=amountToGive)
        await inter.response.send_message(embed=embed)

    ### MEMBER COMMANDS[END]

    ### Admin Commands[START]

    # Tells the command runner the amount of coins within the server
    @slash_command(name="coins-In-Circulation", description="See the total amount of coins within the guild.")
    async def totalCoinsInCirculation(self, inter):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Grabs the minimum moderation role
        for (role) in record:
            modRole = int(role)

        modRole = inter.guild.get_role(modRole)  # Gets the role object

        if inter.author.top_role < modRole:  # If the authors highest role in the guild heirarchy is lower than the moderator role, fail and return a message
            await inter.response.send_message("You do not have permission to use this command.")
            return

        balrecords = db.records("SELECT balance FROM economy WHERE (GuildID) = (?)", inter.guild.id)  # Grabs all of the coins within the guild from the database

        totalCoins = 0

        for (balance) in balrecords:
            res = functools.reduce(lambda sub, ele: sub * 10 + ele, balance)
            totalCoins = totalCoins + res

        await inter.response.send_message(f"There is currently {totalCoins} in circulation in {inter.guild.name}.")

    # See all balances and who's account they are in
    @slash_command(name="see-All-Balances", description="See all of the members and their balance.")
    async def seeAllBalances(self, inter):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Grab the lowest moderator role from the database
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)  # Get the role object

        if inter.author.top_role < modRole:  # Checks if the authors highest role is lower than the moderation role, if not, send a error message
            await inter.response.send_message("You do not have permission to use this command.")
            return

        balrecords = db.records("SELECT * FROM economy WHERE (GuildID) = (?)", inter.guild.id)  # Grab all data from the database for that guild

        # Create an embed showing all of the balances
        embed = Embed(title="All Balances", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        for GuildID, UserID, Balance in balrecords:
            mem = inter.guild.get_member(UserID)  # Get the member object
            if Balance != 0:  # If balance does not equal 0, add a field with that users data to the embed
                embed.add_field(name=mem.name, value=Balance, inline=False)
        await inter.response.send_message(embed=embed)  # Send the embed

    # Give or remove a specified amount of coins from the selected user
    @slash_command(name="give-Or-Remove-Coins",
                   description="Gives or removes the declared amount of coins to the mentioned member.")
    async def give_or_remove_coins(self, inter, member: Member, amount: int):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if inter.author.top_role < modRole:  # Checks if the authors highest role is lower than the moderation role, if not, send a error message
            await inter.response.send_message("You do not have permission to use this command.")
            return
        record = db.record("SELECT maxCoinsInCirculation FROM guildSettings WHERE (GuildID) = (?)", inter.guild.id)  # Grabs the max coins allowed in server param
        for (output) in record:
            maxCoins = output

        totalCoins = await checkAllCoins(inter)
        coins = totalCoins + amount
        if coins > maxCoins:  # If coins is over max coins, send a error message and return
            await inter.response.send_message(
                f"You cannot give that many coins as it surpasses the total amount of coins allowed in circulation('{maxCoins}'). Current amount of coins in circulation is '{totalCoins}'.")
            return

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           member.id)  # Grab the balance of the selected member from the database
        if record is None:  # If balance is None, open an account for the member
            await openAccount(inter.guild.id, member.id)
        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              member.id)  # Grab the balance of the selected member from the database
        for (balance) in balRecord:
            memberBalance = balance

        emojiRecord = db.record("SELECT coinEmoji FROM guildSettings WHERE (GuildID) = (?)", inter.guild.id)  # Grab the coin emoji from the database

        for (emoji) in emojiRecord:
            coinEmoji = emoji
        if coinEmoji is None:
            coinEmoji = ":dollar:"

        amountToGive = memberBalance + amount

        if amount < 0:
            determineText = "removed from"
            amount = str(amount)
            amount = amount.replace("-", "")
            amount = int(amount)
            if memberBalance - amount < 0:
                await inter.response.send_message("You cannot remove that many coins.")
                return
        else:
            determineText = "given to"

        # Create and send an removal or added embed
        em = Embed(title=f"{amount} coins {determineText} {member.name}", color=disnake.Color.dark_teal())
        em.add_field(name="New balance", value=f"{amountToGive} {coinEmoji}")
        em.add_field(name="By: ", value=inter.author.mention)
        em.set_thumbnail(url=member.avatar)
        await inter.response.send_message(embed=em)

        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?, ?)", amountToGive, inter.guild.id,
                   member.id)  # Update the database with the new balance
        db.commit()
        await logs.Logs.give_or_remove_coins_logs(self, inter, inter.author, member, amount)  # Log to the chosen logs channel

    # See the balance of the selected member
    @slash_command(name="see-Balance", description="Check a members balance.")
    async def seeBalance(self, inter, member: Member):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            returns


        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Grab the lowest moderator role
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)  # Get the role object

        if inter.author.top_role < modRole:  # Checks if the authors highest role is lower than the moderation role, if not, send a error message:
            await inter.response.send_message("You do not have permission to use this command.")
            return
        if member.bot is True:  # If the member is a bot, send an error and return.
            await inter.response.send_message("Bots cannot hold coins.")
            return

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           member.id)  # Grab the members balance from the database
        if record is None:  # If balance is None, open an account for the member
            await openAccount(inter.guild.id, member.id)

        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              member.id)  # Grab the members balance from the database

        for (balance) in balRecord:
            memberBalance = balance

        # Create and send an embed with the members balance
        em = Embed(title=f"{member.name}'s balance", color=disnake.Color.dark_teal())
        em.add_field(name="Bank balance", value=memberBalance)
        em.set_thumbnail(url=member.avatar)
        await inter.response.send_message(embed=em)

    ### ADMIN COMMANDS [END]

    ### ADMIN CONFIGURATION COMMANDS [START]

    # Change the max amount of coins that a guild can hold.
    @slash_command(name="change-max-coins", description="Changes the max amount of coins that can be within the guild.")
    async def changeMaxCoins(self, inter, new_amount: int):

        record = db.record("SELECT economyModule FROM guildSettings WHERE GuildID = (?)", inter.guild.id)
        for rec in record:
            moduleStatus = rec

        if moduleStatus == 0: # If economyModule is disabled, send an error and return
            await inter.response.send_message("The economy module is disabled in this guild.")
            return

        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)  # Grabs the lowest moderator role from the database
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)  # Get the role object

        if inter.author.top_role < modRole:  # Checks if the authors highest role is lower than the moderation role, if not, send a error message:
            await inter.response.send_message("You do not have permission to use this command.")
            return

        db.execute("UPDATE guildSettings SET maxCoinsInCirculation = (?) WHERE (GuildID) = (?)", new_amount,
                   inter.guild.id)  # Update the max amount of coins that can be in circulation for the guild
        db.commit()
        await inter.response.send_message(f"Max coins has been changed to {new_amount}.")

    ### ADMIN CONFIGURATION COMMANDS[END]

    ### ERROR HANDLERS[START]

    @totalCoinsInCirculation.error
    async def _totalCoinsInCirculationError(self, inter, exc):
        print(exc)

    ### ERROR HANDLERS[END]


#### YET TO BE IMPLEMENTED

# Version: [0.5.0]
"""
@slash_command(name="shop", scope=889946079188095006, invoke_without_command=False)
    async def Shop(self, inter):
        embed = Embed(title=f"{inter.guild.name} Shop", color=disnake.Color.blue())
        embed.add_field(name="VIP", value="500000 coins")
        embed.add_field(name="VIP+", value="750000 coins")
        await inter.response.send_message(embed=embed)
    
    @Shop.sub_command()
    async def VIP(self, inter):
        await inter.response.send_message("VIP bought")

@slash_command(name="setLotteryPrice", scope=889946079188095006)
    async def setLotteryPrice(self, inter, price: int):
        db.execute("UPDATE guildSettings SET lotteryPrice = (?) WHERE (GuildID) = (?)", price, inter.guild.id)
        db.commit()
        await inter.response.send_message(f"Lottery ticket price set to {price} coins.")
    
    @slash_command(name="endLottery", scope=889946079188095006)
    async def endLottery(self, inter):
        pass

@slash_command(name="buy-lottery-ticket", scope=889946079188095006)
    async def buyLotteryTicket(self, inter):
        pass
"""


def setup(bot):
    bot.add_cog(Economy(bot))
