import asyncio, datetime, json
from discord import Intents
from discord.ext import commands    # discord.py will no longer be maintained. I recommend looking into disnake: https://github.com/DisnakeDev/disnake

import py_tale
from py_tale import Py_Tale

class Vars:                 #This creates variables we can use anywhere
    def __init__(self):
        self.intents = Intents.all()
        self.token = ''
        self.client = commands.Bot(command_prefix='!', intents=self.intents, description='Hello World!!! <3')
        self.guild = None
        self.log_chan = None
        self.player_chunk_timer = {}
        self.discord_info = {}
        self.has_started = False


bot = Py_Tale()        #Instance of Py_Tale stored as bot
my_data = Vars()       #We can access all the variables in class 'Vars' with my_data now.

try:
    with open("./config.json") as f:            #Open config.json in the working directory to read from it
        config = f.read()
        my_data.config = json.loads(config)
        bot.config(client_id=my_data.config["client_id"],  # This function sets our credentials
                   client_secret=my_data.config["client_secret"],
                   scope_string=my_data.config["scope_string"],
                   user_id=my_data.config["user_id"],
                   debug=my_data.config["debug"])
        my_data.token = my_data.config["discord_token"]
except FileNotFoundError:
    print("Failed to find config file! Make sure you make a file called config.json in the same directory at where you run this program!")
    exit()
except Exception as e:
    print(e)
    print("There was an error parsing the json file. Looks like a syntax issue? Please reformat your config.json correctly.")
    exit()

try:
    with open("./discord_info.json") as f:      #Open discord_info.json in the working directory to read from it
        info = f.read()
        my_data.discord_info = json.loads(info)
except FileNotFoundError:
    print("Failed to find discord_info file! Make sure you make a file called discord_info.json in the same directory at where you run this program!")
    exit()
except Exception as e:
    print(e)
    print("There was an error parsing the json file. Looks like a syntax issue? Please reformat your discord_info.json correctly.")
    exit()

async def on_invited(data):                         #This function is called everytime you're invited to a server.
    server_id = int(json.loads(data["content"])["id"])
    await bot.request_accept_invite(server_id)      # Accept all invites indiscriminately

async def on_playerjoin(data):                      #This function is called everytime a player joins
    username = data["data"]["user"]["username"]
    server_id = data["server_id"]
    for k in dict(my_data.discord_info):
        if my_data.discord_info[k]["att_server_id"] == server_id:
            await my_data.client.get_guild(my_data.discord_info[k]["guild_id"]).get_channel(my_data.discord_info[k]["playerjoin_channel"]).send(f"```{username} Joined the server```")


async def on_playerleft(data):                      #This function is called everytime a player leaves
    username = data["data"]["user"]["username"]
    server_id = data["server_id"]
    for k in dict(my_data.discord_info):
        if my_data.discord_info[k]["att_server_id"] == server_id:
            await my_data.client.get_guild(my_data.discord_info[k]["guild_id"]).get_channel(my_data.discord_info[k]["playerjoin_channel"]).send(f"```{username} Left the server```")


async def on_playerkilled(data):                    #This function is called everytime a player is killed
    username = data["data"]["killedPlayer"]["username"]
    server_id = data["server_id"]
    reason = data["data"]["source"]
    f"```{username} was killed by {reason}```"
    for k in dict(my_data.discord_info):
        if my_data.discord_info[k]["att_server_id"] == server_id:
            await my_data.client.get_guild(my_data.discord_info[k]["guild_id"]).get_channel(my_data.discord_info[k]["playerkilled_channel"]).send(f"```{username} was killed by {reason}```")


async def on_playermove(data):                      #This function is called everytime a player moves chunks
    new_chunk =  data["data"]["newChunk"]
    username = data["data"]["player"]["username"]
    server_id = data["server_id"]
    for k in dict(my_data.discord_info):
        if my_data.discord_info[k]["att_server_id"] == server_id:
            if username not in my_data.player_chunk_timer:
                my_data.player_chunk_timer[username] = datetime.datetime.now() - datetime.timedelta(seconds=1)
            if "Cave Layer" in new_chunk:
                if datetime.datetime.now() > my_data.player_chunk_timer[username] + datetime.timedelta(seconds=10):     #This limits 1 message every 10 seconds per player. Prevents spam.
                    my_data.player_chunk_timer[username] = datetime.datetime.now()
                    await bot.send_command_console(server_id, f"player message {username} '{new_chunk}'")   #Message the player in game what layer they're on!
                    await my_data.client.get_guild(my_data.discord_info[k]["guild_id"]).get_channel(my_data.discord_info[k]["chunk_channel"]).send(f"```{username} has entered {new_chunk}```")


@my_data.client.event
async def on_message(message):

    if message.author == my_data.client.user:           #Make sure the bot doesn't respond to itself
        return

    if message.content.startswith("!add server ") and message.author.id == 216680607156011011:  #Make sure only a certain user can use the command
        json_dict = json.loads(message.content.split(" ", maxsplit=2)[2])                       #This command will add a discord server and ATT server for the bot to operate on
        if len(my_data.discord_info) == 0:                                                      #!add server {json format you can find in discord_info.json template}
            my_data.discord_info = json_dict
        else:
            my_data.discord_info = my_data.discord_info | json_dict
        with open('discord_info.json', 'w', encoding='utf-8') as f:
            json.dump(my_data.discord_info, f, ensure_ascii=False, indent=4)
        dict_key = list(json_dict.keys())[0]
        server_id = int(json_dict[dict_key]["att_server_id"])
        await bot.create_console(server_id)
        await message.channel.send("Added server to discord_info.json and created connection")


@my_data.client.event
async def on_ready():               #When the discord bot is fully ready
    if not my_data.has_started:     #This check is necessary because on_ready can be called multiple times. We don't want to reinitialize our ATT bot and create dupe tasks.
        my_data.has_started = True
        print("Discord bot logged in and ready.")
        print("Starting ATT bot")
        asyncio.create_task(bot.run())                  # Start the bot
        await bot.wait_for_ws()                         # Make sure we wait for the main websocket to start.
        invites = await bot.request_invites()           # Get all of our invites to servers on startup
        print("Accepting outstanding invites")
        for x in invites:
            await bot.request_accept_invite(x['id'])    # Accept the invites indiscriminately
        await bot.main_sub(f"subscription/me-group-invite-create/{bot.user_id}", on_invited)   #subscribe to getting invites to groups (This lasts forever)
        print("Creating connections to all server consoles")
        for k in dict(my_data.discord_info):
            try:
                await bot.create_console(my_data.discord_info[k]["att_server_id"])
            except py_tale.ConsolePermissionsDenied as e:
                print("Failed to create console. I'm lacking permission! Ignoring exception:\n", e)
        print("Subscribing to events on all server consoles")
        for k in dict(my_data.discord_info):    #loop through a instanced copy of my_data.discord_info. To make sure we don't change size during iteration.
            try:
                await asyncio.sleep(.1)         #This is placed to prevent super fast spam to the server
                await bot.console_sub("PlayerKilled", on_playerkilled, my_data.discord_info[k]["att_server_id"])
                await bot.console_sub("PlayerMovedChunk", on_playermove, my_data.discord_info[k]["att_server_id"])
                await bot.console_sub("PlayerJoined", on_playerjoin, my_data.discord_info[k]["att_server_id"])
                await bot.console_sub("PlayerLeft", on_playerleft, my_data.discord_info[k]["att_server_id"])
            except Exception as e:
                print(e)
                print(f"Failed to sub to event for guild: '{k}'")   #Just in case we get an error.
        print("Finished initialization. Bot is ready to roll!")

my_data.client.run(my_data.token) #This runs our discord bot
