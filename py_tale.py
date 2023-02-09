# This is the py-tale library, writen by dly2424. For help, inquire at https://discord.gg/GNpmEN2 (The ATT meta discord, a place for bot/dev stuff)
# Please consult the GitHub repository for full documentation, explanation and examples: https://github.com/dly2424/py-tale
try:
    import requests, websockets, asyncio, json, traceback, hashlib
    from datetime import datetime, timedelta
    from colorama import Fore, Style, init  # Colorama is a library for coloring console output. Not mandatory, but looks pretty.
except Exception as e:
    print(e)
    print("You need to install dependencies for py_tale to work. Please install requests, websockets and colorama via pip.")
    print("You should be able to do so with the following commands:")
    print("python -m pip install requests")
    print("python -m pip install websockets")
    print("python -m pip install colorama")
    exit()



init()  # Colorama function call that is required for setting up colors properly.

#Py_tale Exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass

class ConsoleTimeoutException(Error):
    """Exception for when create_console timeouts"""
    pass

class ConsoleAlreadyCreatedException(Error):
    """Exception for when create_console already has that connection open"""
    pass

class ConsoleCreateFailedException(Error):
    """Exception for when create_console fails for an unknown reason"""
    pass

class ConsolePermissionsDenied(Error):
    """Exception for when console info fails due to a lack of permission (or if ID is wrong!)"""
    pass

class FunctionDisabledException(Error):
    """Exception for trying to use an intentionally disabled function"""
    pass

class WrongArgumentTypeException(Error):
    """Exception for passing the wrong object type to a function's parameter"""
    pass

class WrongArgumentFormatException(Error):
    """Exception for using the wrong format with a passed argument to a function's parameter"""
    pass

#Main program
class Py_Tale:

    def __init__(self):  # Function that automatically declares variables
        self.console_websockets = {}
        self.websocket_responses = {}
        self.console_subscriptions = {}
        self.main_subscriptions = {}
        self.cred_initialized = False
        self.user_initialized = False
        self.ws_connected = False
        self.debug = False
        self.id = 0
        self.ws = None
        self.base_url = "https://accounts.townshiptale.com/api"
        self.token_endpoint = "https://accounts.townshiptale.com/connect/token"  # This is the endpoint we use to get our websocket token
        self.websocket_url = "wss://websocket.townshiptale.com"  # This is the url that contains the websocket we connect to.
        self.aws_endpoint = "https://webapi.townshiptale.com"  # This is the endpoint base we use to request info like invites to servers
        self.user_id = ''
        self.client_id = ''
        self.client_secret = ''
        self.scope_string = ''  # scopes should be: ws.group ws.group_members ws.group_servers ws.group_bans ws.group_invites group.info group.join group.leave group.view group.members group.invite server.view server.console
        self.user_name = None
        self.user_password = None
        self.access_token = ''
        self.user_token = ''
        self.expires_in = None
        self.expire_time = None
        self.migrate = False
        self.migrate_token = None
        self.jsonResponse = {}
        self.ws_headers = {}
        self.user_headers = {}
        self.data = {
            'grant_type': 'client_credentials',
            'scope': self.scope_string,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

    async def new_console_websocket(self, addr, port, server_id, token): # Uses SERVER id. - verified
        try:
            async with websockets.connect(f"ws://{addr}:{port}", open_timeout=100) as websocket:  # This is ws protocol not wss
                await websocket.send(token)
                if self.debug:
                    print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (console {server_id} websocket)> {token}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                    print(str(datetime.now()).split(".")[0], "||", f"Console websocket for server {server_id} started!")
                token_response = await websocket.recv()
                token_response = json.loads(token_response)
                self.console_websockets[server_id] = websocket
                if self.debug:
                    print(Fore.GREEN + str(datetime.now()).split(".")[0], "||", f"[RECEIVED] (console {server_id} websocket)< {token_response}", end=Style.RESET_ALL + "\n")
                if server_id in self.console_subscriptions:
                    if len(self.console_subscriptions[server_id]) > 0:
                        for x in self.console_subscriptions[server_id]:
                            to_send = f'{{"id":{self.increment()},"content":"websocket subscribe {x}"}}'
                            await websocket.send(to_send)
                            if self.debug:
                                print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (console {server_id} websocket)> {to_send}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                while True:
                    var = await websocket.recv()
                    var = json.loads(var)
                    if var["type"] == "CommandResult":
                        self.websocket_responses[int(var["commandId"])] = var
                        if self.debug:
                            print(Fore.GREEN + str(datetime.now()).split(".")[0], "||", f"[RECEIVED] (console {server_id} websocket)< {var}", end=Style.RESET_ALL + "\n")
                        continue
                    if server_id in self.console_subscriptions:
                        if var["eventType"] in self.console_subscriptions[server_id]:
                            for function in self.console_subscriptions[server_id][var["eventType"]]:
                                var["server_id"] = server_id
                                asyncio.create_task(function(var))  # call each function and pass the data.
                        if self.debug:
                            print(Fore.GREEN + str(datetime.now()).split(".")[0], "||", f"[RECEIVED] (console {server_id} websocket)< {var}", end=Style.RESET_ALL + "\n")
                if self.debug:
                    print(Fore.RED + str(datetime.now()).split(".")[0], "||", f"Console websocket for server {server_id} closed.", end=Style.RESET_ALL + "\n")  # This should never be called, but just in case.
        except Exception as e:
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", f"Server console {server_id} failed. Error details listed below:\n", e, end=Style.RESET_ALL + "\n")
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", "The server likely shutdown. I'll try to start the console again when the server is back up!", end=Style.RESET_ALL + "\n")
            if server_id in self.console_websockets:
                del self.console_websockets[server_id]

    async def ensure_console(self, data):
        parsed = json.loads(data["content"])
        if "online_ping" in parsed:
            server_id = parsed["id"]
            if server_id not in self.console_websockets:
                if self.debug:
                    print(str(datetime.now()).split(".")[0], "||", f"Group: {parsed['group_id']} with server ID: {parsed['id']}: server has started")
                asyncio.create_task(self.create_console(server_id))

    async def create_console(self, server_id, ensure_open=False, timeout=10, body='{"should_launch":"false","ignore_offline":"false"}'): # Uses SERVER id. - verified
        try:
            timeout = timeout*100 #convert the seconds into the int we use to check time
            server_id = int(server_id)
            if server_id in self.console_websockets:
                raise ConsoleAlreadyCreatedException(f"Console {server_id} is already opened. Cannot create a new console for this server.")
            console_res = requests.post(f"{self.aws_endpoint}/api/servers/{server_id}/console", headers=self.ws_headers, data=body)
            if console_res.status_code != 200:
                raise ConsolePermissionsDenied("Lacking permission to use this console. Is it the right ID? Are you a moderator or owner?")
            console_res = console_res.content.decode('utf-8')
            console_res = json.loads(console_res)
            if console_res["allowed"]:
                addr = console_res["connection"]["address"]
                port = console_res["connection"]["websocket_port"]
                token = console_res["token"]
                asyncio.create_task(self.new_console_websocket(addr, port, server_id, token))
            data = await self.request_server_by_id(server_id)
            if "group_id" in data:
                group_id = data["group_id"]
            else:
                raise ConsoleCreateFailedException(f"Server {server_id} connection rejected. Could not gather data with request_server_by_id.")
            if len(self.main_subscriptions) != 0:
                for iterate in dict(self.main_subscriptions):         # {sub:{"callbacks":[callbacks], "fullname":"Fullnamehere"}}
                    if f"subscription/group-server-status/{group_id}" in self.main_subscriptions[iterate]["fullname"]:
                        if self.ensure_console not in self.main_subscriptions[iterate]["callbacks"]:
                            await self.main_sub(f"subscription/group-server-status/{group_id}", self.ensure_console)
                    else:
                        await self.main_sub(f"subscription/group-server-status/{group_id}", self.ensure_console)
            else:
                await self.main_sub(f"subscription/group-server-status/{group_id}", self.ensure_console)
        except Exception as e:
            raise ConsoleCreateFailedException(f"Failed to create console for server {server_id}. Ensure your bot is a moderator member of the ATT server. Error:\n {e}")
        while server_id not in self.console_websockets and ensure_open:
            await asyncio.sleep(.01)
            timeout -= 1
            if timeout <= 0:
                print(self.console_websockets)
                raise ConsoleTimeoutException(f"Failed to create console for {server_id}. I'll start it when the server goes up.")
        return

    async def get_console_subs(self):
        return self.console_subscriptions

    async def console_unsub(self, sub, server_id=None): # Uses SERVER id. - verified
        if server_id == None:
            for k, v in self.console_websockets:
                if sub in self.console_subscriptions[k]:
                    content = f'{{"id":{self.increment()},"content":"websocket unsubscribe {sub}"}}'
                    await v.send(content)
                    del self.console_subscriptions[k][sub]
                    if self.console_subscriptions[k] == {}:
                        del self.console_subscriptions[k]
        else:
            server_id = int(server_id)
            del self.console_subscriptions[server_id][sub]
            if self.console_subscriptions[server_id] == {}:
                del self.console_subscriptions[server_id]
            content = f'{{"id":{self.increment()},"content":"websocket unsubscribe {sub}"}}'
            await self.console_websockets[server_id].send(content)

    async def console_sub(self, sub, callback, server_id=None): # Uses SERVER id. - verified
        if server_id == None:
            for k, v in self.console_websockets:
                await asyncio.sleep(.025)
                content = f'{{"id":{self.increment()},"content":"websocket subscribe {sub}"}}'
                await v.send(content)
                if self.debug:
                    print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", str(datetime.now()).split(".")[0], "||", f"[SENT] (console {k} websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                if k not in self.console_subscriptions:
                    self.console_subscriptions[k] = {}
                if sub not in self.console_subscriptions[k]:
                    self.console_subscriptions[k][sub] = [callback] #{server_id: {"playerkilled": [callbacks], "PlayerMovedChunk": [callbacks]}}
                else:
                    if callback not in self.console_subscriptions[server_id][sub]:
                        self.console_subscriptions[k][sub].append(callback)
        else:
            await asyncio.sleep(.025) # Limit sending speed slightly.
            server_id = int(server_id)
            content = f'{{"id":{self.increment()},"content":"websocket subscribe {sub}"}}'
            if server_id in self.console_websockets:
                await self.console_websockets[server_id].send(content)
                if self.debug:
                    print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (console {server_id} websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
            if server_id not in self.console_subscriptions:
                self.console_subscriptions[server_id] = {}
            if sub not in self.console_subscriptions[server_id]:
                self.console_subscriptions[server_id][sub] = [callback]
            else:
                if callback not in self.console_subscriptions[server_id][sub]:
                    self.console_subscriptions[server_id][sub].append(callback)

    async def send_command_console(self, server_id, content): # Uses SERVER id. - verified
        i = self.increment()
        content = f'{{"id":{i},"content":"{content}"}}'
        self.websocket_responses[i] = None
        await self.console_websockets[int(server_id)].send(content)
        return await self.responder(i)

    async def get_active_consoles(self):
        return self.console_websockets

    async def responder(self, id):
        response = None
        while True:
            if self.websocket_responses[id] != None:
                response = self.websocket_responses[id]
                break
            await asyncio.sleep(.1)
        del self.websocket_responses[id]
        return response

    async def request_temp_token(self):  # Function that gets token info for our websocket. Also gets a new token before the current one expires. (migrates websocket)
        self.ws_headers = {}
        if self.debug:
            print(str(datetime.now()).split(".")[0], "||", "Obtaining new credentials!")
        response = requests.post(self.token_endpoint, data=self.data)   # Here we request an access token using our config data.
        self.jsonResponse = response.json()  # Turn into dict           # We need to do this to get a token for the websocket.
        self.access_token = self.jsonResponse['access_token']
        self.expires_in = self.jsonResponse['expires_in']
        self.ws_headers["Content-Type"] = "application/json"
        self.ws_headers["x-api-key"] = "2l6aQGoNes8EHb94qMhqQ5m2iaiOM9666oDTPORf"
        self.ws_headers["User-Agent"] = self.client_id
        self.ws_headers["Authorization"] = f"Bearer {self.jsonResponse['access_token']}"
        self.ws_headers["grant_type"] = "client_credentials"
        self.cred_initialized = True
        self.expires_in = int(self.jsonResponse['expires_in'])
        self.expire_time = datetime.now() + timedelta(seconds=self.expires_in-(60*10))

    async def request_user_token(self):  # Function that gets token info for our websocket. Also gets a new token before the current one expires. (migrates websocket)
        try:
            self.user_headers = {}
            if self.debug:
                print(str(datetime.now()).split(".")[0], "||", "Obtaining new user credentials!")
            headers = {"Content-Type": "application/json", "x-api-key": "2l6aQGoNes8EHb94qMhqQ5m2iaiOM9666oDTPORf", "User-Agent": self.client_id, "Accept": "*/*", "Accept-Encoding": "gzip, deflate, br", "Connection": "keep-alive"}
            if len(self.user_password) != 128:
                passhash = hashlib.sha512(self.user_password.encode("UTF-8")).hexdigest()
            else:
                passhash = self.user_password
            body = str({"username":self.user_name, "password_hash":passhash})
            response = requests.post("https://webapi.townshiptale.com/api/sessions", headers=headers, data=body)
            json_response = response.json()
            self.user_token = json_response['access_token']
            self.user_headers["Content-Type"] = "application/json"
            self.user_headers["x-api-key"] = "2l6aQGoNes8EHb94qMhqQ5m2iaiOM9666oDTPORf"
            self.user_headers["User-Agent"] = self.client_id
            self.user_headers["Authorization"] = f"Bearer {self.user_token}"
            self.user_initialized = True
        except Exception as e:
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", "Failed to get user credentials, are your username and password correct?\n", e, end=Style.RESET_ALL + "\n")
            exit()

    async def request_post_console(self, server_id, body='{"should_launch":"false","ignore_offline":"false"}'): # Uses SERVER id. - verified
        await self.wait_for_ready()
        console_res = requests.post(f"{self.aws_endpoint}/api/servers/{server_id}/console", headers=self.ws_headers, data=body)
        if console_res.status_code != 200:
            raise ConsolePermissionsDenied("Lacking permission to use this console. Is it the right ID?")
        console_res = console_res.content.decode('utf-8')
        console_res = json.loads(console_res)
        return console_res

    async def request_ban_player(self, group_id, player_id):
        await self.wait_for_ready()
        ban = requests.post(f"{self.aws_endpoint}/api/groups/{group_id}/bans/{player_id}", headers=self.ws_headers)
        print(ban.status_code, ban.content)
        ban = ban.content.decode('utf-8')
        ban = json.loads(ban)
        return ban

    async def request_unban_player(self, group_id, player_id):
        await self.wait_for_ready()
        unban = requests.delete(f"{self.aws_endpoint}/api/groups/{group_id}/bans/{player_id}", headers=self.ws_headers)
        unban = unban.content.decode('utf-8')
        unban = json.loads(unban)
        return unban

    async def request_group_bans(self, group_id):
        await self.wait_for_ready()
        ban_list = requests.get(f"{self.aws_endpoint}/api/Groups/{group_id}/bans", headers=self.ws_headers)
        ban_list = ban_list.content.decode('utf-8')
        ban_list = json.loads(ban_list)
        return ban_list

    async def request_user_discord(self, player_id):    #may not be possible via bot, instead a user may need to do this
        return FunctionDisabledException("Looks like devs/mods only have permissions to get discords from players...")
        await self.wait_for_ready()
        user_discord = requests.get(f"{self.aws_endpoint}/api/Account/discord/{player_id}", headers=self.user_headers)
        print(user_discord.status_code)
        user_discord = user_discord.content.decode('utf-8')
        print(user_discord)
        user_discord = json.loads(user_discord)
        return user_discord

    async def request_linked_accounts(self, player_id):
        await self.wait_for_ready()
        user_links = requests.get(f"{self.aws_endpoint}/api/linked/{player_id}/linked", headers=self.user_headers)
        user_links = user_links.content.decode('utf-8')
        user_links = json.loads(user_links)
        return user_links

    async def request_recent_players(self, server_id):
        return FunctionDisabledException("request_recent_players works, but doesn't actually provide any data at all. Unfortunate.")
        await self.wait_for_ready()
        recent = requests.get(f"{self.aws_endpoint}/api/recent-players/server/{server_id}", headers=self.user_headers)
        print(recent.content, recent.status_code)
        recent = recent.content.decode('utf-8')
        recent = json.loads(recent)
        return recent

    async def request_user_stats(self, player_id):    #may not be possible via bot, instead a user may need to do this
        return FunctionDisabledException("request_user_stats does not work. Must be a dev only command...")
        await self.wait_for_ready()
        user_stats = requests.get(f"{self.aws_endpoint}/api/Users/{player_id}/statistics", headers=self.user_headers)
        print(user_stats.status_code, user_stats.content)
        user_stats = user_stats.content.decode('utf-8')
        user_stats = json.loads(user_stats)
        return user_stats

    async def request_pending_requests(self, group_id):
        await self.wait_for_ready()
        pending_requests = requests.get(f"{self.aws_endpoint}/api/Groups/{group_id}/requests", headers=self.ws_headers)
        pending_requests = pending_requests.content.decode('utf-8')
        pending_requests = json.loads(pending_requests)
        return pending_requests

    async def request_to_join(self, group_id):
        return FunctionDisabledException("request_to_join Not possible for bot accounts... Which is kinda the whole idea... So yeah...")
        await self.wait_for_ready()
        join = requests.post(f"{self.aws_endpoint}/api/Groups/{group_id}/requests", headers=self.ws_headers)
        print(join.status_code, join.content)
        join = join.content.decode('utf-8')
        join = json.loads(join)
        return join

    async def request_member_info(self, group_id, player_id):
        await self.wait_for_ready()
        member = requests.get(f"{self.aws_endpoint}/api/Groups/{group_id}/members/{player_id}", headers=self.ws_headers)
        member = member.content.decode('utf-8')
        member = json.loads(member)
        return member

    async def request_check_pending_invites(self, group_id):
        await self.wait_for_ready()
        pending_requests = requests.get(f"{self.aws_endpoint}/api/Groups/{group_id}/invites", headers=self.ws_headers)
        pending_requests = pending_requests.content.decode('utf-8')
        pending_requests = json.loads(pending_requests)
        return pending_requests

    async def request_approve_invite(self, group_id, player_id):  # Does not work. Going to have to check this... response 405
        await self.wait_for_ready()
        code = requests.post(f"{self.aws_endpoint}/api/groups/{group_id}/requests/{player_id}", headers=self.ws_headers)
        if code.content.decode('utf-8') == "" or code.content.decode('utf-8') == None:
            code = {"result":"Error, player/group not found", "failed":True}
        else:
            code = {"result":code.content.decode('utf-8'), "failed":False}
        return code

    async def request_decline_invite(self, group_id, player_id):  # Maybe working? Untested. Probably fails too.
        await self.wait_for_ready()
        code = requests.delete(f"{self.aws_endpoint}/api/groups/{group_id}/requests/{player_id}", headers=self.ws_headers)
        if code.content.decode('utf-8') == "" or code.content.decode('utf-8') == None:
            code = {"result":"Error, player/group not found", "failed":True}
        else:
            code = {"result":code.content.decode('utf-8'), "failed":False}
        return code

    async def request_invite_player_id(self, group_id, player_id):  # Uses GROUP id. - verified
        await self.wait_for_ready()                                 # Invites a player to join the specified group
        code = requests.post(f"{self.aws_endpoint}/api/groups/{group_id}/invites/{player_id}", headers=self.ws_headers)
        code = code.content.decode('utf-8')
        code = json.loads(code)
        return code

    async def request_uninvite_player_id(self, group_id, player_id):    # Uses GROUP id. - verified
        await self.wait_for_ready()                                     # Revokes a player's invite to join a server
        code = requests.delete(f"{self.aws_endpoint}/api/groups/{group_id}/invites/{player_id}", headers=self.ws_headers)
        code = code.content.decode('utf-8')
        code = json.loads(code)
        return code

    async def request_server_by_id(self, server_id): # Uses SERVER id. - verified
        await self.wait_for_ready()
        server_info = requests.get(f"{self.aws_endpoint}/api/servers/{server_id}", headers=self.ws_headers)
        server_info = server_info.content.decode('utf-8')
        server_info = json.loads(server_info)
        return server_info

    async def request_server_by_name(self, server_name): # same as request_server_by_id but with a string name.
        await self.wait_for_ready()
        server_info = requests.get(f"{self.aws_endpoint}/api/servers/name/{server_name}", headers=self.ws_headers)
        server_info = server_info.content.decode('utf-8')
        server_info = json.loads(server_info)
        return server_info

    async def request_group_by_id(self, group_id): # Uses GROUP id. - verified
        await self.wait_for_ready()
        group_info = requests.get(f"{self.aws_endpoint}/api/Groups/{group_id}", headers=self.ws_headers)
        group_info = group_info.content.decode('utf-8')
        group_info = json.loads(group_info)
        return group_info

    async def request_accept_invite(self, group_id):    # Uses GROUP id. - verified
        await self.wait_for_ready()                     # Accepts an invite to a server
        accept = requests.post(f"{self.aws_endpoint}/api/groups/invites/{group_id}", headers=self.ws_headers)
        accept = accept.content.decode('utf-8')
        accept = json.loads(accept)
        return accept

    async def request_reject_invite(self, group_id):    # Uses GROUP id. - verified
        await self.wait_for_ready()                     # Rejects an invite to a server
        reject = requests.delete(f"{self.aws_endpoint}/api/groups/invites/{group_id}", headers=self.ws_headers)
        reject = reject.content.decode('utf-8')
        reject = json.loads(reject)
        return reject

    async def request_current_groups(self):
        groups_list = requests.get(f"{self.aws_endpoint}/api/groups/joined?limit=1000", headers=self.ws_headers)
        groups_list = groups_list.content.decode('utf-8')
        groups_list = json.loads(groups_list)
        return groups_list

    async def request_members(self, group_id): # Uses GROUP id. - verified
        await self.wait_for_ready()
        members_list = requests.get(f"{self.aws_endpoint}/api/groups/{group_id}/members", headers=self.ws_headers)
        members_list = members_list.content.decode('utf-8')
        members_list = json.loads(members_list)
        return members_list

    async def request_invites(self):
        await self.wait_for_ready()
        invites_list = requests.get(f"{self.aws_endpoint}/api/groups/invites?limit=1000", headers=self.ws_headers)
        invites_list = invites_list.content.decode('utf-8')
        invites_list = json.loads(invites_list)
        return invites_list

    async def request_search_username(self, username): # Bots can't do this apparently... (but users can!)
        if self.user_initialized:
            await self.wait_for_ready()
            body = '{"username":"' + username + '"}'
            player_info = requests.post(f"{self.aws_endpoint}/api/users/search/username", headers=self.user_headers, data=body)
            player_info = json.loads(player_info.content)
            return player_info
        else:
            raise FunctionDisabledException("request_search_name currently does not work for bot accounts. You'll need to add a user login to the config function.")

    async def request_search_userid(self, player_id): # Bots can't do this apparently... (but users can!)
        if self.user_initialized:
            await self.wait_for_ready()
            player_info = requests.get(f"{self.aws_endpoint}/api/users/{player_id}", headers=self.user_headers)
            player_info = json.loads(player_info.content)
            return player_info
        else:
            raise FunctionDisabledException("request_search_userid currently does not work for bot accounts. You'll need to add a user login to the config function.")

    async def request_user_permissions(self, player_id):
        return FunctionDisabledException("request_user_permissions Dev only command...")
        user_perms = requests.get(f"{self.aws_endpoint}/api/Users/{player_id}/permissions", headers=self.user_headers)
        print(user_perms.content, user_perms.status_code)
        user_perms = user_perms.content.decode('utf-8')
        user_perms = json.loads(user_perms)
        return user_perms

    async def request_change_member_role(self, group_id, player_id, role_int):  # 1 is member, 2 is moderator and 7 is owner role.
        return FunctionDisabledException("request_change_member_role Bot accounts do not seem capable of doing this... Making a user able to do it would be meaningless...")
        change_role = requests.post(f"{self.aws_endpoint}/api/Groups/{group_id}/members/{player_id}/role/{role_int}", headers=self.ws_headers)
        change_role = change_role.content.decode('utf-8')
        change_role = json.loads(change_role)
        return change_role

    async def request_user_achievements(self, player_id):
        return FunctionDisabledException("request_user_achievements is a dev only command seemingly...")
        user_achievements = requests.get(f"{self.aws_endpoint}/api/users/{player_id}/achievements", headers=self.user_headers)
        print(user_achievements.content,user_achievements.status_code)
        user_achievements = user_achievements.content.decode('utf-8')
        user_achievements = json.loads(user_achievements)
        return user_achievements

    async def request_check_user_role(self, group_id, player_id, role_int):
        body = f"{{\"permissions\":[{role_int}]}}"
        user_perms = requests.post(f"{self.aws_endpoint}/api/Groups/{group_id}/{player_id}/permissions/check", headers=self.ws_headers, data=body)
        user_perms = user_perms.content.decode('utf-8')
        user_perms = json.loads(user_perms)
        return user_perms

    async def request_consoles(self):
        await self.wait_for_ready()
        consoles_list = requests.get(f"{self.aws_endpoint}/api/servers/console", headers=self.ws_headers)
        consoles_list = consoles_list.content.decode('utf-8')
        consoles_list = json.loads(consoles_list)
        return consoles_list

    async def ws_send(self, content):  # Function that sends and nicely displays data we are sending over the websocket
        await self.wait_for_ready()
        content = str(content)
        await self.ws.send(content)
        if self.debug:
            print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT]> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color

    def increment(self): #This is an internally used function, not meant to be called by users of the library.
        self.id += 1     #Calling this however, would not break the library :3
        return self.id

    async def main_unsub(self, sub):
        await self.wait_for_ws()
        if not isinstance(sub, str):
            raise WrongArgumentTypeException("main_sub: sub must be string")
        sub_name = sub.split("/")[1]
        if len(sub.split("/")) != 3:
            raise WrongArgumentFormatException("main_sub: wrong subscription format. Example format: subscription/group-server-status/{server_id} or subscription/me-group-invite-create/{client_id}")
        i = self.increment()
        content = f'{{"id": {i}, "method": "DELETE", "path": "{sub}", "authorization": "{self.ws_headers["Authorization"]}"}}'
        await self.ws.send(content)
        if self.debug:
            print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (main websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
        if sub_name in self.main_subscriptions:
            del self.main_subscriptions[sub_name]
        self.websocket_responses[i] = None
        return await self.responder(i)

    async def main_sub(self, sub, callback):    #subscription/group-server-status/{group_id}
        await self.wait_for_ws()                #subscription/{sub}/{self.client_id}
        if not isinstance(sub, str):
            raise WrongArgumentTypeException("main_sub: sub must be string")
        sub_name = sub.split("/")[1]
        if len(sub.split("/")) != 3:
            raise WrongArgumentFormatException("main_sub: wrong subscription format. Example format: subscription/group-server-status/{server_id} or subscription/me-group-invite-create/{client_id}")
        i = self.increment()
        content = f'{{"id": {i}, "method": "POST", "path": "{sub}", "authorization": "{self.ws_headers["Authorization"]}"}}'
        await self.ws.send(content)
        if self.debug:
            print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (main websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
        if sub_name not in self.main_subscriptions:
            self.main_subscriptions[sub_name] = {"callbacks":[callback], "fullname": sub}
        else:
            if callback not in self.main_subscriptions[sub_name]["callbacks"]:
                self.main_subscriptions[sub_name]["callbacks"].append(callback)
        self.websocket_responses[i] = None
        return await self.responder(i)

    async def send_command_main(self, content):
        raise FunctionDisabledException("send_command_main: This has been disabled due to being untested and unneeded. Remove the raise FunctionDisabledException line at the top of the function in py_tale to use.")
        i = self.increment()
        content = f'{{"id":{i},"content":"{content}"}}'
        self.websocket_responses[i] = None
        await self.ws.send(content)
        if self.debug:
            print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (main websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
        return await self.responder(i)

    async def run_ws(self):
        await self.wait_for_ready()
        create = True
        try:
            async with websockets.connect(self.websocket_url, extra_headers=self.ws_headers, open_timeout=100) as websocket:
                self.ws_connected = True
                if not self.migrate:
                    self.ws = websocket
                    print(str(datetime.now()).split(".")[0], "||", "Main websocket started!") ###############
                    if len(self.main_subscriptions) > 0:
                        for iterate in self.main_subscriptions:
                            fullname = self.main_subscriptions[iterate]["fullname"]
                            i = self.increment()
                            to_send = f'{{"id": {i}, "method": "POST", "path": "{fullname}", "authorization": "{self.ws_headers["Authorization"]}"}}'
                            await websocket.send(to_send)
                            if self.debug:
                                print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (main websocket)> {to_send}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                elif self.migrate:
                    self.migrate = False
                    if self.migrate_token == None:  #This if section prevents a rare bug where the migration token is not yet received before migration happens.
                        timeout = 10                #timeout in seconds
                        timeout = timeout*10        #timeout converted to int we use for while loop
                        if self.debug:
                            print(Fore.RED + "Migration token not received yet! Activating counter-measures...", end=Style.RESET_ALL + "\n")
                        while self.migrate_token == None and timeout > 0:
                            await asyncio.sleep(.1)
                            timeout -= 1
                        if self.migrate_token == None:
                            if self.debug:
                                print(Fore.RED + "Looks like the migration token can't be received. Using locally stored variable as backup! All subscriptions should be restored.", end=Style.RESET_ALL + "\n")
                            for iterate in self.main_subscriptions:
                                fullname = self.main_subscriptions[iterate]["fullname"]
                                i = self.increment()
                                to_send = f'{{"id": {i}, "method": "POST", "path": "{fullname}", "authorization": "{self.ws_headers["Authorization"]}"}}'
                                await websocket.send(to_send)
                                if self.debug:
                                    print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (main websocket)> {to_send}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                        else:
                            if self.debug:
                                print(Fore.RED + "Migration token received. Continuing!", end=Style.RESET_ALL + "\n")
                    data = str({"id": self.increment(), "method": "POST", "path": "migrate", "content": self.migrate_token, "authorization": f"{self.ws_headers['Authorization']}"})
                    if self.debug:
                        print(str(datetime.now()).split(".")[0], "||", "migrated")
                    await websocket.send(data)
                    self.ws = websocket
                    if self.debug:
                        print(Fore.CYAN + str(datetime.now()).split(".")[0], "||", f"[SENT] (main websocket)> {data}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                while True:
                    try:
                        var = await websocket.recv()
                        var = json.loads(var)                               #Implement unsubscribing on old websocket? Maybe next verison, I don't think it's an issue.
                        if "key" in var:
                            if var["key"] == "GET /ws/migrate":
                                try:
                                    if int(var["responseCode"]) == 200:
                                        self.migrate_token = var["content"]
                                    else:
                                        print(Fore.RED + "Error in migrate response: Ignoring new key. I will perform a manual migrate instead. (non-200 response code)", end=Style.RESET_ALL + "\n")
                                except Exception as e:
                                    if self.debug:
                                        print(Fore.RED + f"Error in migrate response: Ignoring new key. I will perform a manual migrate instead. ({e})", end=Style.RESET_ALL + "\n")
                        if self.ws is websocket:                    #Only listen to subscriptions if the websocket is the latest websocket. Safety check for preventing double subscriptions if migrate fails while two websockets are open.
                            if "id" in var and "event" in var:
                                if var["event"] == "response" and int(var["id"]) in self.websocket_responses:
                                    self.websocket_responses[int(var["id"])] = var
                                if var["event"] in self.main_subscriptions:
                                    for function in self.main_subscriptions[var["event"]]["callbacks"]:
                                        asyncio.create_task(function(var))
                            if self.debug:
                                print(Fore.GREEN + str(datetime.now()).split(".")[0], "||", f"[RECEIVED] (main websocket)< {var}", end=Style.RESET_ALL + "\n")
                        if datetime.now() >= self.expire_time and create:
                            self.migrate_token = None
                            await self.ws_send({"id": self.increment(), "method": "GET", "path": "migrate", "authorization": f"{self.ws_headers['Authorization']}"})
                            create = False
                            self.migrate = True
                            await self.request_temp_token()
                            if self.user_initialized:
                                await self.request_user_token()
                            if self.debug:
                                print(str(datetime.now()).split(".")[0], "||", "migrating...")
                            asyncio.create_task(self.run_ws())
                    except websockets.ConnectionClosedOK:
                        if self.debug:
                            print(str(datetime.now()).split(".")[0], "||", "old websocket expired.")
                        return
                    except Exception:
                        traceback.print_exc()
                        print("\n" + Fore.RED + str(datetime.now()).split(".")[0], "||", "There was an error in the main websocket. See above. I will try to start it again in 1 minute", end=Style.RESET_ALL + "\n\n")
                        await asyncio.sleep(60)
                        self.migrate = False
                        asyncio.create_task(self.run_ws())
                        return
        except asyncio.TimeoutError:
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", "Main websocket timeout (Is your connection working?) restarting in one minute...", end=Style.RESET_ALL + "\n")
            await asyncio.sleep(60)
            asyncio.create_task(self.run_ws())
            return

    def config(self, client_id, client_secret, scope_string, user_id, debug=False, user_name=None, user_password=None):
        self.user_name = user_name
        self.user_password = user_password
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope_string = scope_string
        self.user_id = user_id
        self.debug = debug
        self.data = {
            'grant_type': 'client_credentials',
            'scope': self.scope_string,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        if user_password != None:
            if len(user_password) != 128: # Lazy way of checking if passed password is a hash or plain text.
                print(Fore.RED + "Warning! It is recommended to use a sha512 hash of your password, rather than plain text.\nContinuing as normal...", end=Style.RESET_ALL + "\n")

    async def ping_websocket(self):  # Function to periodically ping the websocket to keep connection alive.
        try:
            while not self.cred_initialized:
                await asyncio.sleep(1)
            while self.cred_initialized:
                await asyncio.sleep(10)
                await self.ws_send("ping!")  # Sends ping, it's an invalid command, but keeps the connection alive.
                await asyncio.sleep(4 * 60)  # Wait 4 minutes
        except Exception:
            print(str(datetime.now()).split(".")[0], "||", "ping_websocket failed. Restarting it in 1 minute...")
            await asyncio.sleep(60)
            await self.ping_websocket()

    async def wait_for_ready(self):
        if self.user_name == None and self.user_password == None:
            while not self.cred_initialized:
                await asyncio.sleep(1)
        else:
            while not self.cred_initialized and not self.user_initialized:
                await asyncio.sleep(1)

    async def wait_for_ws(self):
        while not self.ws_connected:
            await asyncio.sleep(1)

    async def run(self):
        try:
            asyncio.create_task(self.run_ws())
        except:
            traceback.print_exc()
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", "Failed at task create_task() in Py_tale.", end=Style.RESET_ALL + "\n")
            exit()

        try:
            asyncio.create_task(self.request_temp_token())
        except:
            traceback.print_exc()
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", "Failed at task request_temp_token() in Py_tale.", end=Style.RESET_ALL + "\n")
            exit()

        try:
            if self.user_name != None and self.user_password != None:
                asyncio.create_task(self.request_user_token())
        except:
            traceback.print_exc()
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", "Failed at task request_user_token() in Py_tale.", end=Style.RESET_ALL + "\n")
            exit()

        await self.wait_for_ws()
        try:
            await self.ping_websocket()
        except:
            traceback.print_exc()
            print(Fore.RED + str(datetime.now()).split(".")[0], "||", "Failed at task ping_websocket() in Py_tale.", end=Style.RESET_ALL + "\n")
            exit()