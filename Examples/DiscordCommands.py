import asyncio
from discord import Intents
from discord.ext import commands
from py_tale import Py_Tale

global Has_already_started  # Make a global variable
Has_already_started = False

##############################       This example is trash, but a good reference i guess? I recommend CoolDiscordStuff.py or Py_Bot     #############################################

token = 'OsebBEB345345%DY4.YbBbrRA.brb5h-abBREBEBREBR4545459OBjs'
intents = Intents.all()

client = commands.Bot(command_prefix='!', intents=intents, description='Hello World!!! <3')
bot = Py_Tale()
bot.config(client_id='client_f4be445-34e5-4be41d-abe40-15yb5b5yb4d',         # This function sets our credentials
           user_id=453894589,
           scope_string='ws.group ws.group_members ws.group_servers ws.group_bans ws.group_invites group.info group.join group.leave group.view group.members group.invite server.view server.console',
           client_secret='huuhiGYgyugy667ft67f67fv67876fvut6f7y8A==',
           debug=True)

async def on_invited(data):                         # This is called everytime we get an invite to the server.
    server_id = data["content"]["id"]
    print("I've been invited to group:", server_id)
    await bot.request_accept_invite(server_id)      # This py_tale function accepts the invite
    print("Accepted invite to:", server_id)

@client.event
async def on_message(message):      # Called every time there is a message in discord.

    if message.author == client.user:       # This is so the bot doesn't respond to itself ever.
        return

    if message.content.startswith("!getconsoles"):      # Returns the consoles and corresponding websockets
        await bot.wait_for_ws()                         # Usage: !getconsoles
        consoles = await bot.get_active_consoles()
        await message.channel.send(consoles)

    if message.content.startswith("!command "):                         # Sends a manual command to a server and prints the response
        server_id = int(message.content.split(" ")[1].strip())          # Usage: !command {server_id} player kill dly2424
        command = message.content.split(" ", maxsplit=2)[2].strip()
        content = await bot.send_command_console(server_id, command)    # py_tale function that returns a dictionary of the response from the sent command
        await message.channel.send(content)

    if message.content.startswith("!where "):           # Gets the vector3 position of a player from a server
        server_id = message.content.split(" ")[1]       # Usage: !where {server_id} dly2424
        username = message.content.split(" ")[2]
        result = await bot.send_command_console(server_id, f'player detailed {username}')
        position_of_player = result["data"]["Result"]["Position"]
        await message.channel.send(f'Vector3 position of {username} is: {position_of_player}')

    if message.content.startswith("!startserver "):         # Starts a websocket console for a specified server
        await bot.wait_for_ws()                             # Usage: !startserver {server_id}
        server_id = message.content.split("!startserver ")[1]
        print(server_id)
        await bot.create_console(int(server_id))            # This py_tale function currently does not return anything.

    if message.content.startswith("!subtoinvite"):          # Subscribes to events where the bot is invited to a server.
        await bot.wait_for_ws()
        await bot.main_sub(f"subscription/me-group-invite-create/{bot.user_id}", on_invited)    # py_tale function that calls on_invited() everytime we get an invite.



@client.event
async def on_ready():                   # When the discord bot is fully ready
    global Has_already_started          # Ensure that the variable is global
    if not Has_already_started:         # Check if we've already started (since this function can be called multiple times)
        print("Discord bot ready.")
        asyncio.create_task(bot.run())  # start the bot in a non-blocking coroutine
        Has_already_started = True


client.run(token)   # This runs our discord bot
