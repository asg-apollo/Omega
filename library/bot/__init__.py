from asyncio import sleep
from glob import glob
from colorama import Fore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from disnake import Intents, Forbidden
import disnake
from disnake.ext import ipc, commands
from disnake.ext.commands import Bot as BotBase, Context, BadArgument, MissingRequiredArgument
from disnake.ext.commands import CommandNotFound, when_mentioned_or

from ..db import db

OWNER_IDS = [279283820354863104]
COGS = [path.split("\\")[-1][:-3] for path in glob("./library/cogs/*.py")]


#       OUTDATED[Yet To Be Removed] Pre 0.0.5
# def get_prefix(bot, message):
#     prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
#     return when_mentioned_or(prefix)(bot, message)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ipc = ipc.Server(self, secret_key="apollo")  # Creates an IPC server for the Dashboard
        self.ready = False  # Marks bot as currently not ready
        self.scheduler = AsyncIOScheduler()  # Creates an instance of the scheduler
        self.cogs_ready = Ready()  # Creates an instance of the Ready() function

        db.autosave(self.scheduler)  # Autosaves the database

        super().__init__(
            # command_prefix=get_prefix, # OUTDATED[YET TO BE REMOVED] PRE 0.0.5
            owner_ids=OWNER_IDS,
            intents=Intents.all()  # Enables all intents for the bot
        )

    def run(self, version):
        self.VERSION = version

        print("Running setup")
        self.setup()

        with open("./library/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()  # Reads the token

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    def setup(self):
        for cog in COGS:  # Loads each module individually
            self.load_extension(f"library.cogs.{cog}")
            print(f" {cog} cog loaded")
        print("Setup complete")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO guildSettings (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        # to_remove = []
        # stored_members = db.column("SELECT UserID FROM exp")
        # for id_ in stored_members:
        #     if not self.guild.member(id):
        #         to_remove.append(id_)
        #
        # db.multiexec("DELETE FROM exp WHERE UserID = ?",
        #              ((id,) for id in to_remove))

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

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)

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
            self.scheduler.start()

            self.update_db()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            # EXP SYSTEM [CURRENTLY NOT IMPLENTED, NOR PLANNED]
            # db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
            #              ((member.id,) for guild in self.guilds for member in guild.members if not member.bot))

            self.ready = True
            print("bot ready")
            game = disnake.Activity(type=disnake.ActivityType.listening, name="commands.")  # Sets bots activity to "Listening to commands."
            await bot.change_presence(activity=game)  # Changes to the set activity
            printAllGuilds()
        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.update_db()
        print(f"{Fore.LIGHTBLUE_EX}Omega Joined{Fore.GREEN} {guild.name}!!")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.update_db()
        print(f"{Fore.RED}Omega was removed from {guild.name}!!")


bot = Bot()

def printAllGuilds():
    for guild in bot.guilds:
        print(f"NAME: {guild.name} ID: {guild.id} MEMBER COUNT: {guild.member_count}")


### DASHBOARD ROUTES ###

@bot.ipc.route()
async def get_guild_count(data):
    return len(bot.guilds)


@bot.ipc.route()
async def get_guild_ids(data):
    final = []
    for guild in bot.guilds:
        final.append(guild.id)
    return final  # return guild ids to client


@bot.ipc.route()
async def get_guild(data):
    guild = bot.get_guild(data.guild_id)
    if guild is None: return None

    guild_data = {
        "name": guild.name,
        "id": guild.id,
        "icon_url": guild.icon.url
    }
    return guild_data


@bot.ipc.route()
async def get_cogs(data):
    cogs_list = []
    for cog in bot.cogs:
        cogs_list.append(cog)
    return cogs_list


@bot.ipc.route()
async def get_server_data(data):
    guild = bot.get_guild(data.guild_id)
    if guild is None: return None
    channel_count = 0
    category_count = 0
    for channel in guild.channels:
        channel_count += 1
    for category in guild.categories:
        category_count += 1

    creation_date = str(guild.created_at.year) + "/" + str(guild.created_at.month) + "/" + str(guild.created_at.day)

    server_data = {
        "member_count": guild.member_count,
        "channel_count": channel_count,
        "category_count": category_count,
        "owner": guild.owner.name,
        "creation_date": creation_date
    }
    return server_data


@bot.ipc.route()
async def enable_module(data):
    db.execute(f"UPDATE guildSettings SET {data.module}Module = (?) WHERE GuildID = (?)", 1, data.guild_id)


bot.ipc.start()
