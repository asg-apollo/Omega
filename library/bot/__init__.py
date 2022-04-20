from asyncio import sleep

from discord import Intents, Forbidden
from glob import glob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase, Context, BadArgument, MissingRequiredArgument, command, has_permissions
from discord.ext.commands import CommandNotFound, when_mentioned_or
from ..db import db

OWNER_IDS = [279283820354863104]
COGS = [path.split("\\")[-1][:-3] for path in glob("./library/cogs/*.py")]


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.guild = 889946079188095006
        self.scheduler = AsyncIOScheduler()
        self.cogs_ready = Ready()

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def run(self, version):
        self.VERSION = version

        print("Running setup")
        self.setup()

        with open("./library/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"library.cogs.{cog}")
            print(f" {cog} cog loaded")
        print("Setup complete")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.member(id):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?",
                     ((id,) for id in to_remove))

        db.commit()

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send("I'm not ready to receive commands. Please wait for a few seconds!")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")
        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif isinstance(exc, BadArgument):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            pass

        elif isinstance(exc.original, Forbidden):
            await ctx.send("I do not have the permission to do that!")

        elif hasattr(exc, "original"):
            raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:

            self.guild = self.get_guild(928484198283632701)
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
                         ((member.id,) for guild in self.guilds for member in guild.members if not member.bot))

            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
