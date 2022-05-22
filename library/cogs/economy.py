import functools
import json
from datetime import datetime

import disnake
from disnake import Embed, Member, TextInput
from disnake.ext.commands import Cog, slash_command

from library.cogs import logs
from library.db import db


async def openAccount(GuildID, UserID):
    print("Opening account")
    db.execute("INSERT OR IGNORE INTO economy (GuildID, UserID) VALUES(?,?)", GuildID, UserID)
    db.commit()


async def checkAllCoins(inter):
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
            self.bot.cogs_ready.ready_up("economy")

    @slash_command(name="balance", description="Checks the members balance.")
    async def balance(self, inter):
        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           inter.author.id)
        if record is None:
            await openAccount(inter.guild.id, inter.author.id)

        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              inter.author.id)

        for (balance) in balRecord:
            memberBalance = balance

        em = Embed(title=f"{inter.author.name}'s balance", color=disnake.Color.blue())
        em.add_field(name="Bank balance", value=memberBalance)
        em.set_thumbnail(url=inter.author.avatar)
        await inter.response.send_message(embed=em)

    # @slash_command(name="shop", scope=889946079188095006, invoke_without_command=False)
    # async def Shop(self, inter):
    #     embed = Embed(title=f"{inter.guild.name} Shop", color=disnake.Color.blue())
    #     embed.add_field(name="VIP", value="500000 coins")
    #     embed.add_field(name="VIP+", value="750000 coins")
    #     await inter.response.send_message(embed=embed)
    #
    # @Shop.sub_command()
    # async def VIP(self, inter):
    #     await inter.response.send_message("VIP bought")

    @slash_command(name="transferCoins",
                   description="Transfers the determined amount of coins to the mentioned member.",
                   scope=889946079188095006)
    async def transferCoins(self, inter, member: Member, amount: int):
        if member.bot is True:
            await inter.response.send_message("You can't give coins to a bot.")
            return

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           inter.author.id)
        if record is None:
            await openAccount(inter.guild.id, inter.author.id)

        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              inter.author.id)
        for (authorBalance) in balRecord:
            authorBalance = authorBalance

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           member.id)
        if record is None:
            await openAccount(inter.guild.id, member.id)

        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              member.id)
        for (memberBalance) in balRecord:
            memberBalance = memberBalance

        amountToRemove = authorBalance - amount
        amountToGive = memberBalance + amount

        if authorBalance - amountToRemove < 0:
            await inter.response.send_message("You do not have enough coins.")
            return
        elif amount < 0:
            await inter.response.send_message("You cannot give a negative amount of coins.")
            return

        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?, ?)", amountToRemove, inter.guild.id,
                   inter.author.id)
        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?, ?)", amountToGive, inter.guild.id,
                   member.id)
        db.commit()
        embed = Embed(title="Updated Balances", color=disnake.Color.dark_teal())
        embed.add_field(name=f"{inter.author.name}'s Balance: ", value=f"{amountToRemove}")
        embed.add_field(name=f"{member.name}'s Balance: ", value=amountToGive)
        await inter.response.send_message(embed=embed)

    # Gambling Commands
    @slash_command(name="buy-lottery-ticket", scope=889946079188095006)
    async def buyLotteryTicket(self, inter):
        pass

    # Admin Commands
    @slash_command(name="coins-in-circulation", scope=889946079188095006)
    async def totalCoinsInCirculation(self, inter):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return

        balrecords = db.records("SELECT balance FROM economy WHERE (GuildID) = (?)", inter.guild.id)

        totalCoins = 0

        for (balance) in balrecords:
            res = functools.reduce(lambda sub, ele: sub * 10 + ele, balance)
            totalCoins = totalCoins + res

        await inter.response.send_message(f"There is currently {totalCoins} in circulation in {inter.guild.name}.")

    @slash_command(name="seeAllBalances", scope=889946079188095006)
    async def seeAllBalances(self, inter):

        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return

        balrecords = db.records("SELECT * FROM economy WHERE (GuildID) = (?)", inter.guild.id)
        embed = Embed(title="All Balances", color=disnake.Color.dark_teal(), timestamp=datetime.now())
        for GuildID, UserID, Balance in balrecords:
            mem = inter.guild.get_member(UserID)
            if Balance != 0:
                embed.add_field(name=mem.name, value=Balance, inline=False)
        await inter.response.send_message(embed=embed)

    @slash_command(name="give-or-remove-coins",
                   description="Gives or removes the declared amount of coins to the mentioned member.",
                   scope=889946079188095006)
    async def give_or_remove_coins(self, inter, member: Member, amount: int):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return
        record = db.record("SELECT maxCoinsInCirculation FROM guildSettings WHERE (GuildID) = (?)", inter.guild.id)
        for (output) in record:
            maxCoins = output

        totalCoins = await checkAllCoins(inter)
        coins = totalCoins + amount
        if coins > maxCoins:
            await inter.response.send_message(
                f"You cannot give that many coins as it surpasses the total amount of coins allowed in circulation('{maxCoins}'). Current amount of coins in circulation is '{totalCoins}'.")
            return

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           member.id)
        if record is None:
            await openAccount(inter.guild.id, member.id)
        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              member.id)
        for (balance) in balRecord:
            memberBalance = balance

        emojiRecord = db.record("SELECT coinEmoji FROM guildSettings WHERE (GuildID) = (?)", inter.guild.id)

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

        em = Embed(title=f"{amount} coins {determineText} {member.name}", color=disnake.Color.dark_teal())
        em.add_field(name="New balance", value=f"{amountToGive} {coinEmoji}")
        em.add_field(name="By: ", value=inter.author.mention)
        em.set_thumbnail(url=member.avatar)
        await inter.response.send_message(embed=em)

        db.execute("UPDATE economy SET balance = (?) WHERE (GuildID, UserID) = (?, ?)", amountToGive, inter.guild.id,
                   member.id)
        db.commit()
        await logs.Logs.give_or_remove_coins_logs(self, inter, inter.author, member, amount)

    @slash_command(name="seeBalance", description="Check a members balance.")
    async def seeBalance(self, inter, member: Member):

        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return
        if member.bot is True:
            await inter.response.send_message("Bots cannot hold coins.")
            return

        record = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                           member.id)
        if record is None:
            await openAccount(inter.guild.id, member.id)

        balRecord = db.record("SELECT balance FROM economy WHERE (GuildID, UserID) = (?, ?)", inter.guild.id,
                              member.id)

        for (balance) in balRecord:
            memberBalance = balance
        em = Embed(title=f"{member.name}'s balance", color=disnake.Color.blue())
        em.add_field(name="Bank balance", value=memberBalance)
        em.set_thumbnail(url=member.avatar)
        await inter.response.send_message(embed=em)

    # @slash_command(name="setLotteryPrice", scope=889946079188095006)
    # async def setLotteryPrice(self, inter, price: int):
    #     db.execute("UPDATE guildSettings SET lotteryPrice = (?) WHERE (GuildID) = (?)", price, inter.guild.id)
    #     db.commit()
    #     await inter.response.send_message(f"Lottery ticket price set to {price} coins.")
    #
    # @slash_command(name="endLottery", scope=889946079188095006)
    # async def endLottery(self, inter):
    #     pass

    @slash_command(name="change-max-coins")
    async def changeMaxCoins(self, inter, new_amount: int):
        record = db.record("SELECT modRole FROM guildSettings WHERE GuildID =?", inter.guild.id)
        for (role) in record:
            modRole = role
            modRole = int(modRole)

        modRole = inter.guild.get_role(modRole)

        if modRole not in inter.author.roles:
            await inter.response.send_message("You do not have permission to use this command.")
            return
        db.execute("UPDATE guildSettings SET maxCoinsInCirculation = (?) WHERE (GuildID) = (?)", new_amount,
                   inter.guild.id)
        db.commit()
        await inter.response.send_message(f"Max coins has been changed to {new_amount}.")


def setup(bot):
    bot.add_cog(Economy(bot))
