import asyncio, datetime, json
from discord import Intents
from discord.ext import commands
from py_tale import Py_Tale

class Vars:                 #This creates variables we can use anywhere
    def __init__(self):
        self.intents = Intents.all()
        self.token = 'nkIubiubIOBiyuoouiyv&G98h9BUIB9byub9v.iG*gvb899by'    #This is a fake token, use your own!
        self.client = commands.Bot(command_prefix='!', intents=self.intents, description='Hello World!!! <3')
        self.cats_server = None
        self.log_chan = None
        self.player_chunk_timer = {}
        self.oof_chan = None
        self.join_chan = None

vars = Vars()       #We can access all of the class 'Vars' variables with vars now.


async def on_invited(data):                         #This function is called everytime you're invited to a server.
    server_id = int(json.loads(data["content"])["id"])
    await bot.request_accept_invite(server_id)      # Accept all invites

async def on_playerjoin(data):                      #This function is called everytime a player joins
    username = data["data"]["user"]["username"]
    await vars.join_chan.send(f"```{username} Joined the server```")    #Sends message to discord channel!

async def on_playerleft(data):                      #This function is called everytime a player leaves
    username = data["data"]["user"]["username"]
    await vars.join_chan.send(f"```{username} Left the server```")      #Sends message to discord channel!

async def on_playerkilled(data):                    #This function is called everytime a player is killed
    print(data)
    username = data["data"]["killedPlayer"]["username"]
    server_id = data["server_id"]
    reason = data["data"]["source"]
    if reason == "Command":
        await vars.oof_chan.send(f"```{username} was smited by God```")         #Sends message to discord channel!
    else:
        await vars.oof_chan.send(f"```{username} was killed by {reason}```")    #Sends message to discord channel!

async def on_playermove(data):                      #This function is called everytime a player moves chunks
    new_chunk =  data["data"]["newChunk"]
    username = data["data"]["player"]["username"]
    server_id = data["server_id"]
    if username not in vars.player_chunk_timer:
        vars.player_chunk_timer[username] = datetime.datetime.now() - datetime.timedelta(seconds=1)
    if "Cave Layer" in new_chunk:
        if datetime.datetime.now() > vars.player_chunk_timer[username] + datetime.timedelta(seconds=10):
            vars.player_chunk_timer[username] = datetime.datetime.now()
            await bot.send_command_console(server_id, f"player message {username} '{new_chunk}'")   #Message the player in game what layer they're on!
            await vars.log_chan.send(f"```{username} has entered {new_chunk}```")                   #Sends cave layer message to discord channel!


@vars.client.event
async def on_message(message):

    if message.author == vars.client.user:           #Make sure the bot doesn't respond to itself
        return

    if message.content.startswith("!getconsoles"):  #Returns the active consoles and corresponding websockets
        await bot.wait_for_ws()
        consoles = await bot.get_active_consoles()
        await message.channel.send(consoles)

    if message.content.startswith("!getsubz"):      #Returns the servers with their subscriptions you have set up
        await bot.wait_for_ws()
        consoles = await bot.get_console_subs()
        await message.channel.send(consoles)

    if message.content.startswith("!command "):                             #Sends a manual command to a server and prints the response
        server_id =int(message.content.split(" ", maxsplit=2)[1].strip())       #Usage: !command {server_id} player kill dly2424
        command = message.content.split(" ", maxsplit=2)[2].strip()
        await bot.wait_for_ws()
        await bot.send_command_console(server_id, command)

    if message.content.startswith("!where "):       #Gets the vector3 position of a player from a server
        username = message.content.split(" ")[1]    #Usage: !where zenzerker {server_id}
        server_id = message.content.split(" ")[2]
        result = await bot.send_command_console(server_id, f'player detailed {username}')
        await message.channel.send(f'Vector3 position of {username}: {result["data"]["Result"]["Position"]}')

    if message.content.startswith("!startserver "): #Starts a websocket console for a specified server
        await bot.wait_for_ws()
        server_id = int(message.content.split("!startserver ")[1])
        await bot.create_console(server_id)


@vars.client.event
async def on_ready(): #When the discord bot is fully ready
    print("ready")
    asyncio.create_task(bot.run()) #start the bot
    vars.cats_server = vars.client.get_guild(24568634455656343)        #Get the discord
4    vars.oof_chan = vars.cats_server.get_channel(8457846578546879754)    #Get certain channel
    vars.join_chan = vars.cats_server.get_channel(4567456856848569478)   #Get certain channel
    await bot.wait_for_ws()
    att_server = 5678959
    await bot.create_console(att_server)       #this will start a connection to this console every time the server starts up
    await asyncio.sleep(4)
    await bot.console_sub("PlayerMovedChunk", on_playermove, server_id=att_server)         #subscribe to player moving chunks event on cats_server (this keeps the sub through server restarts)
    await bot.console_sub("PlayerKilled", on_playerkilled, server_id=att_server)           #subscribe to player dying event on cats_server (this keeps the sub through server restarts)
    await bot.console_sub("PlayerJoined", on_playerjoin, server_id=att_server)             #subscribe to player joining event on cats_server (this keeps the sub through server restarts)
    await bot.console_sub("PlayerLeft", on_playerleft, server_id=att_server)               #subscribe to player leaving event on cats_server (this keeps the sub through server restarts)
    await bot.main_sub(f"subscription/me-group-invite-create/{bot.user_id}", on_invited)   #subscribe to getting invites to groups (This lasts forever)

bot = Py_Tale()
bot.config(client_id='client_nJNui9o90-iNi3-Nunb-9Iu8-IN0oh08hIi',  # This function sets our credentials
           user_id=8983879,                                         # These are fake credentials, use your own!
           scope_string='ws.group ws.group_members ws.group_servers ws.group_bans ws.group_invites group.info group.join group.leave group.view group.members group.invite server.view server.console',
           client_secret='jbIYug8gy86G78vy8yv89yb8b8YV8yyyvg9yv9vVYy99yv8yA==',
           debug=True)

vars.client.run(vars.token) #This runs our discord bot
