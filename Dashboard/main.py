import sqlite3

from quart import Quart, render_template, request, session, redirect, url_for, jsonify
from quart_discord import DiscordOAuth2Session
from disnake.ext import ipc

app = Quart(__name__)
app.config["SECRET_KEY"] = "test123"
app.config["DISCORD_CLIENT_ID"] = "948767251312554095"
app.config["DISCORD_CLIENT_SECRET"] = "ytWTgeeziSMEvc0omc2__atK9R2X7ry3"
app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"
ipc_client = ipc.Client(secret_key="apollo")

discord = DiscordOAuth2Session(app)


@app.route("/")
async def home():
    return await render_template("index.html", authorized=await discord.authorized)


@app.route("/login")
async def login():
    return await discord.create_session(scope=["identify", "email", "guilds"])


@app.route("/callback")
async def callback():
    try:
        await discord.callback()
    except Exception:
        pass
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
async def dashboard():
    if not await discord.authorized:
        return redirect(url_for("login"))

    guild_count = await ipc_client.request("get_guild_count")
    guild_ids = await ipc_client.request("get_guild_ids")

    user_guilds = await discord.fetch_guilds()
    guilds = []

    for guild in user_guilds:
        if guild.permissions.administrator:
            guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
            guilds.append(guild)

    guilds.sort(key=lambda x: x.class_color == "red-border")
    name = (await discord.fetch_user()).name
    return await render_template("dashboard.html", guild_count=guild_count, guilds=guilds, username=name)


@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
    if not await discord.authorized:
        return redirect(url_for("login"))


    guild = await ipc_client.request("get_guild", guild_id=guild_id)
    cogs = await ipc_client.request("get_cogs")
    server_info = await ipc_client.request("get_server_data", guild_id=guild_id)
    print(server_info["member_count"])

    statusDict = {
        "automod": "None",
        "economy": "None",
        "fun": "None",
        "logs": "None",
        "misc": "None",
        "moderation": "None",
        "random": "None",
        "suggestions": "None",
        "welcome": "None"
    }
    moduleStatus = ""
    with sqlite3.connect("C:\\Users\\Ethan\\Documents\\GitHub\\Omega\\data\\db\\database.db") as con:
        cur = con.cursor()
        for cog in cogs:
                record = cur.execute(f"SELECT {cog}Module FROM guildSettings WHERE GuildID = {guild_id}")
                record = cur.fetchone()
                for module in record:
                    isEnabled = str(module)
                    print(isEnabled)
                if isEnabled == "1":
                    statusDict[f"{cog}"] = "Enabled"
                else:
                    statusDict[f"{cog}"] = "Disabled"

    if guild is None:
        return redirect(
            f"https://discord.com/api/oauth2/authorize?client_id={app.config['DISCORD_CLIENT_ID']}&permissions=8&guild_id={guild_id}&redirect_uri={app.config['DISCORD_REDIRECT_URI']}&response_type=code&scope=bot%20applications.commands")
    return await render_template("guild_dashboard.html", guild=guild, cogs=cogs, server_info=server_info, statusDict=statusDict)


@app.route("/dashboard/<int:guild_id>/<string:module>/<statusDict>")
async def dashboard_module(guild_id, module, statusDict=None):
    if not await discord.authorized:
        return redirect(url_for("login"))
    guild = await ipc_client.request("get_guild", guild_id=guild_id)
    return await render_template("module_page.html", guild=guild, module=module, statusDict=statusDict)


@app.route("/dashboard/<int:guild_id>/<string:module>/<statusDict>/enable")
async def enableModule(guild_id, module, statusDict):
    if not await discord.authorized:
        return redirect(url_for("login"))
    guild = await ipc_client.request("get_guild", guild_id=guild_id)
    moduleStatus = ""
    with sqlite3.connect("C:\\Users\\Ethan\\Documents\\GitHub\\Omega\\data\\db\\database.db") as con:
        cur = con.cursor()

        record = cur.execute(f"SELECT {module}Module FROM guildSettings WHERE GuildID = {guild_id}")
        record = cur.fetchone()
        for (number) in record:
            isTrue = number
        if isTrue == 1:
            cur.execute(f"UPDATE guildSettings SET {module}Module = 0 WHERE GuildID = {guild_id}")
            statusDict[module] = "Enabled"
        else:
            cur.execute(f"UPDATE guildSettings SET {module}Module = 1 WHERE GuildID = {guild_id}")
            statusDict[module] = "Disabled"
        con.commit()
    print(statusDict)
    return redirect(url_for(f"dashboard_module", guild_id=guild_id, module=module, statusDict=statusDict))

if __name__ == "__main__":
    app.run(debug=True)
