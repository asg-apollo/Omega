import asyncio
import random
from datetime import datetime
from random import choice, randint
from typing import Optional

import discord
from discord import Embed
from discord.ext.commands import Cog, BadArgument, MissingRequiredArgument
from discord.ext.commands import command

from ..joke_api import Jokes

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi", "hey"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hey', 'Hi', 'Yo'))} {ctx.author.mention}!")

    @command(name="dice")
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))
        if value >= 12:
            await ctx.send("Too many dice rolled.")
            return
        rolls = [randint(1, value) for i in range(dice)]

        await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @command(name="smack", aliases=["slap"])
    async def smack_member(self, ctx, member: discord.Member, *, reason: Optional[str]):
        if reason is None:
            reason = "no reason"

        await ctx.send(f"{ctx.author.mention} smacked {member.mention} for {reason}!")

    @command(name="race")
    async def race_member(self, ctx, member: discord.Member, length: int):
        if member == ctx.author:
            await ctx.send("You can't race yourself!")
            return
        if length > 1000:
            await ctx.send("Selected number is too large. Please select a number under 1000.")
            return


        await ctx.send("Race starting in..")
        await asyncio.sleep(0.3)
        await ctx.send("3")
        await asyncio.sleep(0.3)
        await ctx.send("2")
        await asyncio.sleep(0.3)
        await ctx.send('1')
        await asyncio.sleep(0.3)
        await ctx.send("GO!")

        racer1 = ctx.author
        racer2 = member
        racer1Time = 0
        racer2Time= 0

        if length < 10:
            racer1Time = random.randrange(1, 3)
            racer2Time = random.randrange(1, 3)

        if length > 10 < 20:
            racer1Time = random.randrange(4, 12)
            racer2Time = random.randrange(4, 12)

        if length > 25 < 50:
            racer1Time = random.randrange(8, 15)
            racer2Time = random.randrange(8, 15)
        if length > 50 < 100:
            racer1Time = random.randrange(14, 30)
            racer2Time = random.randrange(14, 30)
        if length > 100 < 300:
            racer1Time = random.randrange(60, 85)
            racer2Time = random.randrange(60, 85)
        if length > 300 < 800:
            racer1Time = random.randrange(180, 240)
            racer2Time = random.randrange(180, 240)
        if length > 800 < 1000:
            racer1Time = random.randrange(360, 440)
            racer2Time = random.randrange(360, 440)

        embed = Embed(title="Race", description=f"Race between {ctx.author.mention} and {member.mention}",
                      timestamp=datetime.utcnow(), color=ctx.author.color)
        embed.add_field(name=f"{ctx.author.display_name} ran {length}m in: ", value=racer1Time)
        embed.add_field(name=f"{member.display_name} ran {length}m in: ", value=racer2Time)
        await ctx.send(embed=embed)
        if racer1Time < racer2Time:
            await ctx.send(
                f"Congratulations {ctx.author.mention} on winning against {member.mention}! Your really fast!")
        if racer2Time < racer1Time:
            await ctx.send(
                f"Congratulations {member.mention} on winning against {ctx.author.mention}! Your really fast!")
        if racer1Time == racer2Time:
            await ctx.send(f"It's a tie between {ctx.author.mention} and {member.mention}!")

    @command(name="joke")
    async def joke(self, ctx):
        j = await Jokes()
        joke = await j.get_joke()

        if joke["type"] == "single":
            await ctx.send(joke["joke"])
        else:
            await ctx.send(joke["setup"] + '\n' + joke["delivery"])

    @joke.error
    async def joke_error(self, ctx, exc):
        if isinstance(exc, KeyError):
            await ctx.send("Try again!")

    @race_member.error
    async def race_member_error(self, ctx, exc):
        if isinstance(exc, MissingRequiredArgument):
            await ctx.send("An parameter(s) is missing.")

    @smack_member.error
    async def smack_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("That member doesn't exist.")
        if isinstance(exc, MissingRequiredArgument):
            await ctx.send("Must specify a member.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
