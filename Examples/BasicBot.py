from py_tale import Py_Tale
import asyncio, json


bot = Py_Tale()

bot.config(client_id = 'client_verw4f4f-3f45-4v4d-ab51-4b5n6nb44b', # This function sets our credentials
            user_id = 39879838,
            scope_string = 'ws.group ws.group_members ws.group_servers ws.group_bans ws.group_invites group.info group.join group.leave group.view group.members group.invite server.view server.console',
            client_secret = 'IG978Kkg789809yBJHjyf8HGIG808jbikBIGIYG97YGYYIiyv7878KGKGhijvyUY79==',
           debug = True)

async def on_playerkilled(data):    # Everytime a player is killed this function gets run. data is a dictionary that contains the event data
    print("Player was killed!:", data)
    username = data["data"]["killedPlayer"]["username"]
    server_id = data["server_id"]
    reason = data["data"]["source"]
    print(f"Player {username} was killed by {reason} on server {server_id}")

async def on_playermove(data):      # Everytime a player moves this function gets run. data is a dictionary that contains the event data
    print("Player moved:", data)
    new_chunk =  data["data"]["newChunk"]
    username = data["data"]["player"]["username"]
    server_id = data["server_id"]
    print(f"Player {username} moved to chunk {new_chunk} on server {server_id}")

async def on_invited(data):         # Everytime we get an invite to a server this function gets run. data is a dictionary that contains the event data
    print("I was invited:", data)
    server_id = int(json.loads(data["content"])["id"])
    print(f"Recieved invitation to server {server_id}")
    await bot.request_accept_invite(server_id)    # Accept all invites
    print("Accepted the invite.")

async def main():
    asyncio.create_task(bot.run())                  # Run the bot
    await bot.wait_for_ws()                         # This waits until the main websocket is ready
    invites = await bot.request_invites()           # Get all of our invites to servers
    for x in invites:
        await bot.request_accept_invite(x['id'])    # Accept all invites
    await bot.main_sub("subscription/me-group-invite-create/" + str(bot.user_id), on_invited) # Subscribe to know when we get invited
    await bot.create_console(457468463)             # Start the connection to the server 457468463's console
    for x in await bot.get_active_consoles():       # For every server we have opened with (bot.create_console)
        await bot.console_sub("PlayerKilled", on_playerkilled, server_id=x)         # Subscribe to when players get killed. Execute on_playerkilled when someone dies.
        await bot.console_sub("PlayerMovedChunk", on_playermove, server_id=x)       # Subscribe to when players move chunks. Execute on_playermove when someone moves chunks.
    print(await bot.get_console_subs())                                             # Just shows what we have for current subscriptions
    while True:
        await asyncio.sleep(1)  # Sleep forever and let the bot do it's thing

asyncio.run(main())     #Runs the main function
