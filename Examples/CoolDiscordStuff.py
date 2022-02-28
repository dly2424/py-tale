import asyncio, datetime, json
from discord import Intents
from discord.ext import commands
from py_tale import Py_Tale

class Vars:
    def __init__(self):
        self.intents = Intents.all()
        self.token = 'BKHJkuiuyg79877UzNTM0NzIw.din-Q.kjshdi78yDui970_Dijs9BBuy9o'    #Discord token (This one's fake, use your own!)
        self.client = commands.Bot(command_prefix='!', intents=self.intents, description='Hello World!!! <3')
        self.cats_server = None
        self.log_chan = None
        self.player_chunk_timer = {}
        self.oof_chan = None
        self.join_chan = None

vars = Vars()


async def on_invited(data):                             #This function is called everytime you're invited to a server.
    server_id = int(json.loads(data["content"])["id"])  #Accepts invite upon receiving.
    await bot.request_accept_invite(server_id)

async def on_playerjoin(data):                      #This function is called everytime a player joins
    username = data["data"]["user"]["username"]     #Sends a message to a discord channel when someone joins
    await vars.join_chan.send(f"```{username} Joined the server```")

async def on_playerleft(data):                      #This function is called everytime a player leaves
    username = data["data"]["user"]["username"]     #Sends a message to a discord channel when someone leaves
    await vars.join_chan.send(f"```{username} Left the server```")

async def on_playerkilled(data):                        #This function is called everytime a player is killed
    username = data["data"]["killedPlayer"]["username"] #Sends a discord message to a channel when a player dies and cause of death
    server_id = data["server_id"]
    reason = data["data"]["source"]
    if reason == "Command":
        await vars.oof_chan.send(f"```{username} was smited by God```")
    else:
        await vars.oof_chan.send(f"```{username} was killed by {reason}```")

async def on_playermove(data):                      #This function is called everytime a player moves chunks
    new_chunk =  data["data"]["newChunk"]           #Sends a message to a discord channel when a player enters a cave layer with it's layer n
    username = data["data"]["player"]["username"]   #Also sends a message to the player in-game what layer they're on upon entering a new layer
    server_id = data["server_id"]
    if username not in vars.player_chunk_timer:
        vars.player_chunk_timer[username] = datetime.datetime.now() - datetime.timedelta(seconds=1)
    if "Cave Layer" in new_chunk:
        if datetime.datetime.now() > vars.player_chunk_timer[username] + datetime.timedelta(seconds=10):
            vars.player_chunk_timer[username] = datetime.datetime.now()
            await bot.send_command_console(server_id, f"player message {username} '{new_chunk}'")
            await vars.log_chan.send(f"```{username} has entered {new_chunk}```")


@vars.client.event
async def on_message(message):

    if message.author == vars.client.user:          #Make sure the bot doesn't respond to itself
        return

    if message.content.startswith("!getconsoles"):  #Returns the active consoles and corresponding websockets
        await bot.wait_for_ws()
        consoles = await bot.get_active_consoles()
        await message.channel.send(consoles)

    if message.content.startswith("!getsubz"):      #Returns the servers with their subscriptions you have set up
        await bot.wait_for_ws()
        consoles = await bot.get_console_subs()
        await message.channel.send(consoles)

    if message.content.startswith("!command "):                                     #Sends a manual command to a server and prints the response
        server_id = int(message.content.split(" ", maxsplit=2)[1].strip())          #Usage: !command {server_id} player kill dly2424
        command = message.content.split(" ", maxsplit=2)[2].strip()
        await bot.wait_for_ws()
        server_response = await bot.send_command_console(server_id, command)
        await message.channel.send(server_response)

    if message.content.startswith("!where "):               #Gets the vector3 position of a player from a server
        server_id = int(message.content.split(" ")[1])      #Usage: !where {server_id} zenzerker
        username = message.content.split(" ")[2]
        result = await bot.send_command_console(server_id, f'player detailed {username}')
        await message.channel.send(f'Vector3 position of {username}: {result["data"]["Result"]["Position"]}')

    if message.content.startswith("!startserver "):         #Starts a websocket console for a specified server
        await bot.wait_for_ws()                             #Usage: !startserver {server_id}
        server_id = int(message.content.split("!startserver ")[1])
        await bot.create_console(server_id)

    if message.content.startswith("!check"):                #Checks what you've got for subs to the main websocket
        subs = await bot.get_console_subs()
        await message.channel.send(subs)


@vars.client.event
async def on_ready(): #When the discord bot is fully ready
    print("ready")
    asyncio.create_task(bot.run()) #start the bot
    vars.cats_server = vars.client.get_guild(37797457345733540041)
    vars.log_chan = vars.cats_server.get_channel(824564534574537620)
    vars.oof_chan = vars.cats_server.get_channel(854435725745734886)
    vars.join_chan = vars.cats_server.get_channel(935474575685684758)
    await bot.wait_for_ws()     #Make sure our main websocket is running before continuing...
    my_server = 850508448
    try:
        await bot.create_console(my_server)
    except Exception as e:
        print(e, "\ncouldn't start the server. Probably offline!")
    await asyncio.sleep(4) #Give the server 4 seconds to startup.
    if my_server in await bot.get_active_consoles():
        await bot.console_sub("PlayerMovedChunk", on_playermove, server_id=my_server) #This will only work if the server is running
        await bot.console_sub("PlayerKilled", on_playerkilled, server_id=my_server) #This will only work if the server is running
        await bot.console_sub("PlayerJoined", on_playerjoin, server_id=my_server) #This will only work if the server is running
        await bot.console_sub("PlayerLeft", on_playerleft, server_id=my_server) #This will only work if the server is running
    else:
        print("Didn't start subscriptions. Server wasn't online.")
    await bot.main_sub(f"subscription/me-group-invite-create/{bot.user_id}", on_invited)


bot = Py_Tale()

bot.config(client_id='client_v4e4tg1-3v3r5-fc24-g254-0wv3un098bv83',  # This function sets our credentials
           user_id=8998371,
           scope_string='ws.group ws.group_members ws.group_servers ws.group_bans ws.group_invites group.info group.join group.leave group.view group.members group.invite server.view server.console',
           client_secret='YGuiygUYG8o7Tyg8yVy8vyv8yvuiByv8tvut78Tf8tct87==',
           debug=True)
           
vars.client.run(vars.token) #This runs our discord bot
