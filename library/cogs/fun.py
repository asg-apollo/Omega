import asyncio
import random
from datetime import datetime
from random import choice, randint

import disnake
from disnake import Embed, Interaction
from disnake.ext.commands import Cog, BadArgument, MissingRequiredArgument, slash_command


from ..joke_api import Jokes


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="hello", aliases=["hi", "hey"], description="Says hi!")
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hey', 'Hi', 'Yo'))} {ctx.author.mention}!")

    @slash_command(name="dice", description="Rolls a dice. MUST HAVE A d between the 2 numbers. Example: 3d5")
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))
        if value >= 12:
            await ctx.send("Too many dice rolled.")
            return
        rolls = [randint(1, value) for i in range(dice)]

        await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @slash_command(name="smack", aliases=["slap"], description="Smacks the selected member with an optional reason.")
    async def smack_member(self, ctx, member: disnake.Member, *, reason=''):
        if reason is None:
            reason = "no reason"

        await ctx.send(f"{ctx.author.mention} smacked {member.mention} for {reason}!")

    @slash_command(name="race", description="Race the selected member with a optional distance!")
    async def race_member(self, ctx, member: disnake.Member, length=100):
        length = int(length)
        if member == ctx.author:
            await ctx.send("You can't race yourself!")
            return
        if length > 1000:
            await ctx.send("Selected number is too large. Please select a number under 1000.")
            return

        racer1 = ctx.author
        racer2 = member
        racer1Time = 0
        racer2Time = 0

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

        # if racer1Time < racer2Time:
        #     text = f"Congratulations {ctx.author.mention} on winning against {member.mention}! Your really fast!"
        # if racer2Time < racer1Time:
        #     text = f"Congratulations {member.mention} on winning against {ctx.author.mention}! Your really fast!"
        # if racer1Time == racer2Time:
        #     text = ctx.send(f"It's a tie between {ctx.author.mention} and {member.mention}!")

        three_embed = Embed(title="Timer: 3 seconds!",
                            timestamp=datetime.now(), color=ctx.author.color)
        two_embed = Embed(title="Timer: 2 seconds!",
                          timestamp=datetime.now(), color=ctx.author.color)
        one_embed = Embed(title="Timer: 1 seconds!",
                          timestamp=datetime.now(), color=ctx.author.color)
        go_embed = Embed(title="Go!!",
                         timestamp=datetime.now(), color=ctx.author.color)

        result_embed = Embed(title="Race", description=f"Race between {ctx.author.mention} and {member.mention}",
                             timestamp=datetime.now(), color=ctx.author.color)
        result_embed.add_field(name=f"{ctx.author.display_name} ran {length}m in: ", value=f"{racer1Time} seconds")
        result_embed.add_field(name=f"{member.display_name} ran {length}m in: ", value=f"{racer2Time} seconds", inline=False)

        if racer1Time < racer2Time:
            winner = racer1
            text = f"{winner} won! Congratulations!"
        if racer2Time < racer1Time:
            winner = racer2
            text = f"{winner} won! Congratulations!"
        elif racer1Time == racer2Time:
            winner = "Tie!"
            text = f"It's a tie!"

        result_embed.add_field(name="Winner: ", value=text)

        await ctx.send(embed=three_embed)
        await asyncio.sleep(0.3)
        msg = await Interaction.original_message(ctx)
        await msg.edit(embed=two_embed)
        await asyncio.sleep(0.3)
        await msg.edit(embed=one_embed)
        await asyncio.sleep(0.3)
        await msg.edit(embed=go_embed)
        await asyncio.sleep(0.3)
        await msg.edit(embed=result_embed)
        print("\n Fun: Race over")

    @slash_command(name="joke", description="Provides a random joke!")
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

    @roll_dice.error
    async def roll_dice_error(self, ctx, exc):
        if isinstance(exc, ValueError):
            await ctx.send("An error occurred.")

    @race_member.error
    async def race_member_error(self, ctx, exc):
        if isinstance(exc, MissingRequiredArgument):
            await ctx.send("An parameter(s) is missing.")
            print("missing param")
        else:
            print(exc)

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
