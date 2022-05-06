# Py_tale
## A library for developing ATT bots in Python.

This library is designed to be fully async. This means it is fully compatible with Discord's python library [discord.py](https://discordpy.readthedocs.io/en/latest/api.html) and it's forks.

Make sure to take a look into the /Examples folder! I'm still updating and adding examples. Currently they're unrefined projects that only demonstrate some of the library's capabilities.
#
#
# The goal

The goal of py-tale is to provide an _**easy to read**_, _**easy to use**_ and _**stable**_ platform for development of ATT bots in Python. The library keeps it simple, with asynchronous functions that can be called to get data and perform actions. There are no complicated or unnecessary concepts. The library focuses on freedom to write as you see fit, intermediate to expert programmers alike.

#
#
# How to install

Simply download the py_tale.py file and place it into your main .py directory. You can then do a local import with:

`from py_tale import Py_Tale`

It's that easy!

Though you'll also need some dependencies. `requests`, `websockets` and `colorama`
Install them with these pip commands in your terminal/command prompt!

`python -m pip install requests`

`python -m pip install websockets`

`python -m pip install colorama`

These are not necessary to import in your script. They're only used by Py_tale.
#
#
# How to use
Firstly, create an instance of the Py_Tale class. We'll call this `bot`, though you can call it whatever you want.
`bot` will be used to call all of py_tale's functions and variables.
```
bot = Py_Tale()
```
After that, we'll need to configure our credentials. Using our bot credentials sent to us by Joel, we place them in the `bot.config` function.
```
my_scopes = 'ws.group ws.group_members ws.group_servers ws.group_bans ws.group_invites group.info group.join group.leave group.view group.members group.invite server.view server.console'

#These are fake credentials. Put in your own real ones!
bot.config(client_id='client_sdv98798-vw3r314-afd1-69420smd',
           user_id=89273545,
           scope_string=my_scopes,
           client_secret='IuIB9876adHUWIBIBu89auiBIBu9yw8998w89yd==',
           debug=False) # Debug is optional. Only use True if you'd like to see data being sent to and from Alta's endpoints!
```
From here on out you're ready to start the bot! We can start it with `await bot.run()` or in the background with `asyncio.create_task(bot.run())`
#
#
# Before you start

Make sure you understand the difference between `server_id` and `group_id`. `server_id` refers to Server IDs that can be found on the list of servers on https://dash.townshiptale.com/servers/ where as `group_id` refers to the Group ID that can be found by clicking on your server in the dashboard and looking in your `Server Info` module for "Group".

Using the dashboard is only one way to find out these IDs. There are multiple ways to programatically get the Group and Server IDs through Py_Tale :3

These IDs are different numbers for the same server. When reading the documentation and using these functions, make sure you're using the right ID!
#
#
# Request functions

request functions return dictionary responses and can be used with asyncio's `await`

**Here is a list of all current request functions:**

`bot.request_post_console(server_id, body='{"should_launch":"false","ignore_offline":"false"}')`
> Used for gathering info about a server's console.
```
    Parameters:
        •server_id - the ID number of your server. Int or String object.
        •body (optional!) - default: '{"should_launch":"false","ignore_offline":"false"}' String object.
    Example return:
        {'server_id': 89586948, 'allowed': True, 'was_rejection': False, 'cold_start': False, 'fail_reason': 'Nothing', 'connection': {'server_id': 0, 'address': '23.78.436.17', 'local_address': '127.0.0.1', 'pod_name': 'att-release-ptx57-vvse', 'game_port': 7713, 'console_port': 7020, 'logging_port': 7712, 'websocket_port': 7667, 'webserver_port': 7780}, 'token': 'bv87s4y387b837v4tygo87ygo847tby874t8ogb7t8o7e54ytgb897ybtg87h438b7w3h4897tg38974yt873gybt8973y4bg58973y4gbt8973y4gb5o873ty4gb587t3yg489b7t34857gt3847tyb89374t89734tb98743tgb98743tbg9h8734tbh897'}
```
#
#
`bot.request_server_by_id(server_id)`
> Used for gathering info about a server.
```
    Parameters:
        •server_id - the ID number of your server. Int or String object.
    Example return:
        {'id': 93247934798, 'name': "Dlys awesome server", 'online_players': [], 'server_status': 'Online', 'final_status': 'Online', 'scene_index': 0, 'target': 1, 'region': 'north-america-agones', 'last_online': '2022-02-27T22:04:24.5444317Z', 'description': "Dlys private server.", 'playability': 0.0, 'version': 'main-0.0.79.7', 'group_id': 89586948, 'owner_type': 'Group', 'owner_id': 201274988, 'type': 'Normal', 'fleet': 'att-release', 'up_time': '7.09:36:59.0452399'}
```
#
#
`bot.request_current_groups()`
> Used for getting all groups you're currently a member of. - Note: This one returns a list of dictionaries!
```
    Example return:
        [{'group': {'servers': [{'id': 3457637, 'name': "Dlys awesome server", 'scene_index': 0, 'status': 'Online'}], 'allowed_servers_count': 1, 'roles': [{'role_id': 1, 'name': 'Member', 'permissions': ['Invite'], 'allowed_commands': []}, {'role_id': 2, 'name': 'Moderator', 'permissions': ['Invite', 'AcceptInvite', 'Kick', 'Console'], 'allowed_commands': []}, {'role_id': 7, 'name': 'Owner', 'color': '#00bcd4', 'permissions': ['Invite', 'AcceptInvite', 'Ban', 'Kick', 'CreateServer', 'ModifyGroup', 'ModifyServer', 'Console', 'ControlServer', 'ManageRoles'], 'allowed_commands': []}], 'id': 3445567768, 'name': "Dlys Group", 'description': "Dlys private server.", 'member_count': 19, 'created_at': '2021-06-12T22:05:39.1118498Z', 'type': 'Private', 'tags': []}, 'member': {'group_id': 34354658785, 'user_id': 24423654, 'username': 'My_Bot', 'bot': True, 'icon': 0, 'permissions': 'Moderator', 'role_id': 2, 'created_at': '2022-02-23T05:06:02.196Z', 'type': 'Accepted'}}]
```
#
#
`bot.request_accept_invite(group_id)`
> Used to accept an invite to a server
```
    Parameters:
        •group_id - the ID number of your group. Int or String object.
    Example return:
        {"group_id":123546432,"user_id":8938789,"username":"My_Bot","bot":True,"icon":0,"permissions":"Member","role_id":1,"created_at":"2022-02-27T20:54:52.144Z","type":"Accepted"}
```
#
#
`bot.request_reject_invite(group_id)`
> Used to refuse an invite to a server
```
    Parameters:
        •group_id - the ID number of your group. Int or String object.
    Example return:
        {"group_id":123546432,"user_id":8938789,"username":"My_Bot","bot":True,"icon":0,"permissions":"Member","role_id":1,"created_at":"2022-02-27T23:28:15.534Z","type":"Left"}'
```
#
#
`bot.request_invite_player_id(group_id, player_id)`
> Used to invite a player to join the specified group
```
    Parameters:
        •group_id - the ID number of your group. Int or String object.
        •player_id - the ID number of the player to invite. Int or String object
    Example return:
        {'group_id': 24367535, 'user_id': 547463573, 'username': 'Dly2424', 'bot': False, 'icon': 0, 'permissions': 'Member', 'role_id': 1, 'created_at': '2022-03-01T06:17:44.7434669Z', 'type': 'Invited'}
```
#
#
`bot.request_uninvite_player_id(group_id, player_id)`
> Used to revoke a player's invite to join a server
```
    Parameters:
        •group_id - the ID number of your group. Int or String object.
        •player_id - the ID number of the player to revoke invite. Int or String object
    Example return:
        {'group_id': 24367535, 'user_id': 547463573, 'username': 'Dly2424', 'bot': False, 'icon': 0, 'permissions': 'Member', 'role_id': 1, 'created_at': '2022-03-01T06:17:44.743Z', 'type': 'Kicked'}
```
#
#
`bot.request_members(group_id)`
> Used to get members of a server - Note: This one returns a list of dictionaries!
```
    Parameters:
        •group_id - the ID number of your group. Int or String object.
    Example return:
        [{'group_id': 4356745743678, 'user_id': 3465443532, 'username': 'dly', 'bot': False, 'icon': 0, 'permissions': 'Member, Moderator, Admin', 'role_id': 7, 'created_at': '2021-06-14T23:48:30.393Z', 'type': 'Accepted'}, {'group_id': 4356745743678, 'user_id': 985437643, 'username': 'cora', 'bot': False, 'icon': 0, 'permissions': 'Member', 'role_id': 1, 'created_at': '2021-06-14T23:52:27.485Z', 'type': 'Accepted'}, {'group_id': 4356745743678, 'user_id': 3245671435435, 'username': 'My_Bot', 'bot': True, 'icon': 0, 'permissions': 'Member', 'role_id': 1, 'created_at': '2022-02-27T23:52:30.191Z', 'type': 'Accepted'}]
```
#
#
`bot.request_invites()`
> Used to get your current invites to servers - Note: This one returns a list of dictionaries!
```
    Example return:
        [{'invited_at': '2022-02-28T00:31:17.571Z', 'id': 234334546, 'name': "Dlys server", 'description': 'A group for Dly and their friends', 'member_count': 3, 'created_at': '2021-06-14T23:48:30.3139878Z', 'type': 'Private', 'tags': []}]
```
#
#
`bot.request_consoles()`
> Used to get all servers with consoles you currently have permission to use - Note: This one returns a list of dictionaries!
```
    Example return:
        [{'id': 7861354864, 'name': "Dlys awesome server", 'online_players': [], 'server_status': 'Online', 'final_status': 'Online', 'scene_index': 0, 'target': 1, 'region': 'north-america-agones', 'last_online': '2022-02-27T22:04:24.5444317Z', 'description': "Dlys private server.", 'playability': 0.0, 'version': 'main-0.0.79.7', 'group_id': 1325436654, 'owner_type': 'Group', 'owner_id': 201453432, 'type': 'Normal', 'fleet': 'att-release', 'up_time': '7.09:36:59.0452399'}]
```
#
#
`bot.request_search_username(username)`
> Used to resolve the ID of an Alta account from a username. Note: User account required!
```
    Parameters:
        •username - The username to lookup. String object.
    Example return:
        {'id': 98327498, 'username': 'jimmythetrain'}
```
# Other functions

These functions can be called using asyncio's `await`

`bot.create_console(server_id, ensure_open=False, timeout=10, body='{"should_launch":"false","ignore_offline":"false"}')`
> This function will create a websocket connection to a server's console in the background. When the server closes, the connection is killed. 
However this function will automatically connect back when the server starts up again. Currently only returns None.
```
    Parameters:
        •server_id - the ID number of your server. Int object.
        •ensure_open (optional!) - make sure the console connection is open before continuing. This throws an error after the timeout if server is offline. Bool object.
        •timeout (optional!) - the max number in seconds to wait for a successful connection before throwing an Exception. default: 10. Int object.
        •body (optional!) - default: '{"should_launch":"false","ignore_offline":"false"}' String object.
    Example return:
        None
```
#
#
`bot.get_active_consoles()`
> This function returns a dictionary of all server consoles you have open. Returns server ID and websocket object. You can use this to check what consoles are open.
Equivalent of using the bot.console_websockets variable.
```
    Example return:
        {835264448: <websockets.legacy.client.WebSocketClientProtocol object at 0x0000028B08EE78E0>}
```
#
#
`bot.send_command_console(server_id, content)`
> This function can be used to send commands to a server console just like the dashboard does.
```
    Parameters:
        •server_id - the ID number of your server. Int object.
        •content - the command to send to the console. String object
    Example return:
        {'type': 'CommandResult', 'timeStamp': '2022-02-28T02:03:19.178102Z', 'data': {'Command': {'Parameters': [{'Type': 'PlayerList', 'HasDefault': False, 'Default': None, 'Attributes': [], 'Name': 'players', 'FullName': 'players'}], 'IsProgressive': False, 'ReturnType': 'System.Void', 'Priority': 0, 'Aliases': ['kill'], 'FullName': 'player.kill', 'Requirements': [{'TypeId': 'Alta.Console.ServerOnlyAttribute'}], 'Attributes': [], 'Name': 'kill', 'Description': 'Kills a player'}, 'ResultString': 'Success'}, 'commandId': 3}
```
#
#
`bot.console_sub(sub, callback, server_id=None)`
> This function subscribes to an event on a server such as PlayerKilled, must have created a server websocket with bot.create_console first.
This function will automatically re-sub to a server after the connection starts again after having been closed.
When the event occurs, callback will be executed with event data passed to it. Currently only returns None.
```
    Parameters:
        •sub - The event you want to subscribe to. Not case sensitive. String object
        •callback - The function to be called when the event happens. Must take one parameter that the event data gets passed to. Function object
        •server_id (optional!) - If server_id is specified, the event only subscribes to that server. Otherwise, it will subscribe to all currently opened server consoles. Int object
    Example return:
        None
```
#
#
`bot.console_unsub(sub, server_id=None)`
> This function unsubscribes to a subscription on a server. Removes all callbacks for that subscription on that server.
Currently only returns None.
```
    Parameters:
        •sub - The event you want to unsubscribe to. Not case sensitive. String object.
        •server_id (optional!) - If server_id is specified, you only unsubscribe to that event on that exact server. Otherwise, it will unsubscribe that subscription to all currently opened server consoles. Int object.
    Example return:
        None
```
#
#
`bot.get_console_subs()`
> This function returns a dictionary of server IDs with their respective currently subscribed events and callbacks
```
    Example return:
        {335244647: {'playerkilled': [<function on_playerkilled at 0x00000281F85CBA60>]}}
```
#
#
`bot.config(client_id, client_secret, scope_string, user_id, debug=False, user_name=None, user_password=None):`
> This function sets your credentials for the program. 
```
    Parameters:
        •client_id - Your client ID sent to you by Joel. String object
        •client_secret - Your client secret sent to you by Joel. String object
        •scope_string - Your scopes sent to you by Joel. Should be a long string with scopes separated by spaces. String object
        •user_id - Your user ID sent to you by Joel. Int object
        •debug (optional!) - Setting this to True will enable colored printing to console of all data being sent and received by websockets and endpoints. Bool object
        •user_name (optional!) - Setting this along side your user_password will allow you to login to a user account which enables some features that bot accounts normally can't use. String object
        •user_password (optional!) - Use this along side your user_name to login to an Alta user account. This can be plain-text or a sha512 hash. String object
    Example return:
        None
```
#
#
`bot.run()`
> This function starts the bot. Should only be run after bot.config. Most cases you'd want to run this with asyncio.create_task instead of await. Returns None
```
    Example return:
        None
```
#
#
`bot.wait_for_ready()`
> This function just waits for the initialization of the bot's credentials if it already hasn't. Must run bot.run before calling this or it will wait forever.
```
    Example return:
        None
```
#
#
`bot.wait_for_ws()`
> This function just waits for the first main websocket to be open if it already hasn't started. Must run bot.run before calling this or it will wait forever.
```
    Example return:
        None
```
#
#
`bot.main_sub(sub, callback)`
> This function subscribes to events that occur off of servers such as subscription/me-group-request-create/{user_id_here}. Example being when you're invited to a server, or removed from one.
```
    Parameters:
        •sub - The event you want to unsubscribe to. Not case sensitive. String object
        •callback - The function you want to be called and sent event data to when the sub event occurs. Function object
    Example return:
        None
```

#
#
`bot.main_unsub(sub)`
> This function unsubscribes to events that occur off of servers.
```
    Parameters:
        •sub - The event you want to unsubscribe to. Not case sensitive. String object
    Example return:
        {'id': 2, 'event': 'response', 'key': 'DELETE /ws/subscription/me-group-invite-create/900176244', 'content': '', 'responseCode': 200}
```
**All other functions of the Py_tale library are either broken or intended to be disabled.**

# Additional information
List of custom Exceptions
```
py_tale.ConsoleTimeoutException             # used when create_console times out
py_tale.ConsoleAlreadyCreatedException      # used when trying to open a console that's already open
py_tale.ConsoleCreateFailedException        # used when getting a generic error in create_console
py_tale.FunctionDisabledException           # used when trying to call a disabled function
py_tale.WrongArgumentTypeException          # used when you pass an incorrect argument object type to a function
py_tale.WrongArgumentFormatException        # used when you pass an argument that's in the wrong format
py_tale.ConsolePermissionsDenied            # used when you lack permissions to use a console
```
Current list of known subscriptions for server consoles: (Use these in console_sub/console_unsub)
```
PlayerJoined
PlayerLeft
PlayerKilled
PlayerMovedChunk
PlayerStateChanged
TraceLog
DebugLog
InfoLog
WarnLog
ErrorLog
FatalLog
TrialStarted
TrialFinished
TradeDeckUsed
ProfilingData
ObjectKilled
PopulationModified
```
Current list of known subscriptions for main websocket: (Use these in main_sub/main_unsub)
```
subscription/me-group-invite-create/{user_id_here}
subscription/me-group-invite-delete/{user_id_here}
subscription/me-group-request-create/{user_id_here}
subscription/me-group-request-delete/{user_id_here}
subscription/group-server-status/{group_id_here}
subscription/group-server-update/{group_id_here}
subscription/group-server-create/{group_id_here}
subscription/group-server-delete/{group_id_here}
subscription/group-update/{group_id_here}
```


