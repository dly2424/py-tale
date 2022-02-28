# This is the py-tale library, writen by dly2424. For help, inquire at https://discord.gg/GNpmEN2 (The ATT meta discord, a place for bot/dev stuff)
# Please consult the GitHub repository for full documentation, explanation and examples: https://github.com/dly2424/py-tale
try:
    import requests, websockets, asyncio, json, traceback
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


class Py_Tale:

    def __init__(self):  # Function that automatically declares variables
        self.console_websockets = {}
        self.websocket_responses = {}
        self.console_subscriptions = {}
        self.main_subscriptions = {}
        self.cred_initialized = False
        self.ws_connected = False
        self.debug = False
        self.id = 0
        self.ws = None
        self.base_url = "https://accounts.townshiptale.com"
        self.token_endpoint = "https://accounts.townshiptale.com/connect/token"  # This is the endpoint we use to get our websocket token
        self.websocket_url = "wss://5wx2mgoj95.execute-api.ap-southeast-2.amazonaws.com/dev"  # This is the url that contains the websocket we connect to.
        self.aws_endpoint = "https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/"  # This is the endpoint base we use to request info like invites to servers
        self.user_id = ''
        self.client_id = ''
        self.client_secret = ''
        self.scope_string = ''  # scopes should be: ws.group ws.group_members ws.group_servers ws.group_bans ws.group_invites group.info group.join group.leave group.view group.members group.invite server.view server.console
        self.access_token = ''
        self.expires_in = None
        self.expire_time = None
        self.migrate = False
        self.migrate_token = None
        self.jsonResponse = {}
        self.ws_headers = {}
        self.data = {
            'grant_type': 'client_credentials',
            'scope': self.scope_string,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

    async def new_console_websocket(self, addr, port, server_id, token):
        try:
            async with websockets.connect(f"ws://{addr}:{port}", open_timeout=100) as websocket:  # This is ws protocol not wss
                await websocket.send(token)
                self.console_websockets[server_id] = websocket
                print(f"Console websocket for server {server_id} started!")
                while True:
                    var = await websocket.recv()
                    var = json.loads(var)
                    if var["type"] == "CommandResult":
                        self.websocket_responses[int(var["commandId"])] = var
                        print(Fore.GREEN + f"[RECEIVED] (console {server_id} websocket)< {var}", end=Style.RESET_ALL + "\n")
                        continue
                    if server_id in self.console_subscriptions:
                        if var["eventType"] in self.console_subscriptions[server_id]:
                            for function in self.console_subscriptions[server_id][var["eventType"]]:
                                content = json.loads(f"{{'server_id':{server_id},{str(var)[1:]}".replace("'", '"'))
                                asyncio.create_task(function(content))  # call each function and pass the data.
                        if self.debug:
                            print(Fore.GREEN + f"[RECEIVED] (console {server_id} websocket)< {var}", end=Style.RESET_ALL + "\n")
                print(Fore.RED + f"Console websocket for server {server_id} closed.", end=Style.RESET_ALL + "\n")  # This should never be called, but just in case.
        except Exception as e:
            print(traceback.print_exc())
            print(Fore.RED + f"Server console {server_id} failed. Error details listed below:\n", e, end=Style.RESET_ALL + "\n")
            if server_id in self.console_websockets:
                del self.console_websockets[server_id]

    async def create_console(self, server_id, body='{"should_launch":"false","ignore_offline":"false"}'):
        server_id = int(server_id)
        if server_id in self.console_websockets:
            print(f"Console {server_id} is already opened. Cannot create a new console for this server.")
            return
        console_res = requests.post(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/servers/{server_id}/console", headers=self.ws_headers, data=body)
        console_res = console_res.content.decode('utf-8')
        console_res = json.loads(console_res)
        print(console_res)
        if console_res["allowed"]:
            print(console_res)
            addr = console_res["connection"]["address"]
            port = console_res["connection"]["websocket_port"]
            token = console_res["token"]
            asyncio.create_task(self.new_console_websocket(addr, port, server_id, token))
        else:
            raise Exception(f"Server {server_id} connection rejected. Reason: {console_res['fail_reason']}")

    async def get_console_subs(self):
        return self.console_subscriptions

    async def console_unsub(self, sub, server_id=None):
        if server_id == None:
            for k, v in self.console_websockets:
                if sub in self.console_subscriptions[k]:
                    content = f'{{"id":{self.increment()},"content":"websocket unsubscribe {sub}"}}'
                    await v.send(content)
                    del self.console_subscriptions[k][sub]
                    if self.console_subscriptions[k] == {}:
                        del self.console_subscriptions[k]
        else:
            del self.console_subscriptions[server_id][sub]
            if self.console_subscriptions[server_id] == {}:
                del self.console_subscriptions[server_id]
            content = f'{{"id":{self.increment()},"content":"websocket unsubscribe {sub}"}}'
            await self.console_websockets[server_id].send(content)

    async def console_sub(self, sub, callback, server_id=None):
        if server_id == None:
            for k, v in self.console_websockets:
                content = f'{{"id":{self.increment()},"content":"websocket subscribe {sub}"}}'
                await v.send(content)
                if self.debug:
                    print(Fore.CYAN + f"[SENT] (console {k} websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                if k not in self.console_subscriptions:
                    self.console_subscriptions[k] = {}
                if sub not in self.console_subscriptions[k]:
                    self.console_subscriptions[k][sub] = [callback] #{server_id: {"playerkilled": [callbacks], "PlayerMovedChunk": [callbacks]}}
                else:
                    self.console_subscriptions[k][sub].append(callback)
        else:
            content = f'{{"id":{self.increment()},"content":"websocket subscribe {sub}"}}'
            await self.console_websockets[server_id].send(content)
            if self.debug:
                print(Fore.CYAN + f"[SENT] (console {server_id} websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
            if server_id not in self.console_subscriptions:
                self.console_subscriptions[server_id] = {}
            if sub not in self.console_subscriptions[server_id]:
                self.console_subscriptions[server_id][sub] = [callback]
            else:
                self.console_subscriptions[server_id][sub].append(callback)

    async def send_command_console(self, server_id, content):
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
        print("Obtaining new credentials!")
        response = requests.post(self.token_endpoint, data=self.data)   # Here we request an access token using our config data.
        self.jsonResponse = response.json()  # Turn into dict           # We need to do this to get a token for the websocket.
        self.access_token = self.jsonResponse['access_token']
        self.expires_in = self.jsonResponse['expires_in']
        self.ws_headers["Content-Type"] = "application/json"
        self.ws_headers["x-api-key"] = "2l6aQGoNes8EHb94qMhqQ5m2iaiOM9666oDTPORf"
        self.ws_headers["User-Agent"] = self.client_id
        self.ws_headers["Authorization"] = f"Bearer {self.jsonResponse['access_token']}"
        self.cred_initialized = True
        self.expires_in = int(self.jsonResponse['expires_in'])
        self.expire_time = datetime.now() + timedelta(seconds=self.expires_in-(60*10))

    async def request_post_console(self, group_id, body='{"should_launch":"false","ignore_offline":"false"}'):
        await self.wait_for_ready()
        console_res = requests.post(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/servers/{group_id}/console", headers=self.ws_headers, data=body)
        console_res = console_res.content.decode('utf-8')
        console_res = json.loads(console_res)
        return console_res

    async def request_ban_player(self, group_id, player_id):
        raise Exception("request_ban_player: This has been disabled due to console bans being irreversible. Remove the raise Exception line at the top of the function in py_tale to use.")
        await self.wait_for_ready()
        code = requests.post(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/{group_id}/bans/{player_id}", headers=self.ws_headers)
        return code

    async def request_unban_player(self, group_id, player_id):
        raise Exception("request_unban_player: This has been disabled due to console bans being irreversible. Remove the raise Exception line at the top of the function in py_tale to use.")
        await self.wait_for_ready()
        code = requests.delete(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/{group_id}/bans/{player_id}", headers=self.ws_headers)
        return code

    async def request_approve_invite(self, group_id, player_id):  # Maybe working? Untested.
        await self.wait_for_ready()
        code = requests.post(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/{group_id}/requests/{player_id}", headers=self.ws_headers)
        if code.content.decode('utf-8') == "" or code.content.decode('utf-8') == None:
            code = {"result":"Error, player/group not found", "failed":True}
        else:
            code = {"result":code.content.decode('utf-8'), "failed":False}
        return code

    async def request_decline_invite(self, group_id, player_id):  # Maybe working? Untested.
        await self.wait_for_ready()
        code = requests.delete(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/{group_id}/requests/{player_id}", headers=self.ws_headers)
        if code.content.decode('utf-8') == "" or code.content.decode('utf-8') == None:
            code = {"result":"Error, player/group not found", "failed":True}
        else:
            code = {"result":code.content.decode('utf-8'), "failed":False}
        return code

    async def request_invite_player_id(self, group_id, player_id): # Error 403...
        await self.wait_for_ready()
        code = requests.post(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/{group_id}/invites/{player_id}", headers=self.ws_headers)
        return code.content.decode('utf-8')

    async def request_uninvite_player_id(self, group_id, player_id):# Probably doesnt work either
        await self.wait_for_ready()
        code = requests.delete(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/{group_id}/invites/{player_id}", headers=self.ws_headers)
        return code.content.decode('utf-8')

    async def request_server_by_id(self, server_id):
        await self.wait_for_ready()
        server_info = requests.get(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/servers/{server_id}", headers=self.ws_headers)
        server_info = server_info.content.decode('utf-8')
        server_info = json.loads(server_info)
        return server_info

    async def request_accept_invite(self, group_id):
        await self.wait_for_ready()
        accept = requests.post(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/invites/{group_id}", headers=self.ws_headers)
        return accept.content

    async def request_reject_invite(self, group_id):
        await self.wait_for_ready()
        reject = requests.delete(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/invites/{group_id}", headers=self.ws_headers)
        return reject.content

    async def request_current_groups(self):
        groups_list = requests.get(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/joined", headers=self.ws_headers)
        groups_list = groups_list.content.decode('utf-8')
        groups_list = json.loads(groups_list)
        return groups_list

    async def request_members(self, group_id):
        await self.wait_for_ready()
        members_list = requests.get(f"https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/{group_id}/members", headers=self.ws_headers)
        members_list = members_list.content.decode('utf-8')
        members_list = json.loads(members_list)
        return members_list

    async def request_invites(self):
        await self.wait_for_ready()
        invites_list = requests.get("https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/groups/invites?limit=1000", headers=self.ws_headers)
        invites_list = invites_list.content.decode('utf-8')
        invites_list = json.loads(invites_list)
        return invites_list

    async def request_search_name(self, username):
        raise Exception("request_search_name currently does not work. It's not possible for bot accounts to do this.")
        await self.wait_for_ready()
        body = '{"username":"' + username + '"}'
        result = requests.post("https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/users/search/username", headers=self.ws_headers)
        return result

    async def request_consoles(self):
        await self.wait_for_ready()
        consoles_list = requests.get("https://967phuchye.execute-api.ap-southeast-2.amazonaws.com/prod/api/servers/console", headers=self.ws_headers)
        consoles_list = consoles_list.content.decode('utf-8')
        consoles_list = json.loads(consoles_list)
        return consoles_list

    async def ws_send(self, content):  # Function that sends and nicely displays data we are sending over the websocket
        await self.wait_for_ready()
        content = str(content)
        await self.ws.send(content)
        if self.debug:
            print(Fore.CYAN + f"[SENT]> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color

    def increment(self): #This is an internally used function, not meant to be called by users of the library.
        self.id += 1     #Calling this however, would not break the library :3
        return self.id

    async def main_unsub(self, sub):
        await self.wait_for_ws()
        if not isinstance(sub, str):
            raise Exception("main_sub: sub must be string")
        sub_name = sub.split("/")[1]
        if len(sub.split("/")) != 3:
            raise Exception("main_sub: wrong subscription format. Example format: subscription/group-server-status/{server_id} or subscription/me-group-invite-create/{client_id}")
        i = self.increment()
        content = f'{{"id": {i}, "method": "DELETE", "path": "{sub}", "authorization": "{self.ws_headers["Authorization"]}"}}'
        await self.ws.send(content)
        if self.debug:
            print(Fore.CYAN + f"[SENT] (main websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
        if sub_name in self.main_subscriptions:
            del self.main_subscriptions[sub_name]
        self.websocket_responses[i] = None
        return await self.responder(i)

    async def main_sub(self, sub, callback):    #subscription/group-server-status/{server_id}
        await self.wait_for_ws()                #subscription/{sub}/{self.client_id}
        if not isinstance(sub, str):
            raise Exception("main_sub: sub must be string")
        sub_name = sub.split("/")[1]
        if len(sub.split("/")) != 3:
            raise Exception("main_sub: wrong subscription format. Example format: subscription/group-server-status/{server_id} or subscription/me-group-invite-create/{client_id}")
        i = self.increment()
        content = f'{{"id": {i}, "method": "POST", "path": "{sub}", "authorization": "{self.ws_headers["Authorization"]}"}}'
        await self.ws.send(content)
        if self.debug:
            print(Fore.CYAN + f"[SENT] (main websocket)> {content}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
        if sub_name not in self.main_subscriptions:
            self.main_subscriptions[sub_name] = [callback]
        else:
            self.main_subscriptions[sub_name].append(callback)
        self.websocket_responses[i] = None
        return await self.responder(i)

    async def run_ws(self):
        await self.wait_for_ready()
        create = True
        try:
            async with websockets.connect(self.websocket_url, extra_headers=self.ws_headers, open_timeout=100) as websocket:
                self.ws_connected = True
                print("Websocket started!")
                self.ws = websocket
                if self.migrate:
                    self.migrate = False
                    data = str({"id": self.increment(), "method": "POST", "path": "migrate", "content": self.migrate_token, "authorization": f"{self.ws_headers['Authorization']}"})
                    print("migrated")
                    await websocket.send(data) #This is incorrect: [RECEIVED] (main websocket)< {'message': 'Internal server error', 'connectionId': 'OLdqff5iSwMAc9A=', 'requestId': 'OLdqkFOoywMFkbw='}
                    if self.debug:
                        print(Fore.CYAN + f"[SENT] (main websocket)> {data}", end=Style.RESET_ALL + "\n")  # end = Style.RESET_ALL prevents other prints from containing the set color
                while True:
                    try:
                        var = await websocket.recv()
                        var = json.loads(var)
                        #print(var)
                        if "key" in var:
                            if var["key"] == "GET /ws/migrate":
                                self.migrate_token = var["content"]
                                #print(self.migrate_token)
                                #loaded_content = json.loads(var["content"])
                                #self.migrate_token = loaded_content["token"]
                        if "id" in var and "event" in var:
                            if var["event"] == "response" and int(var["id"]) in self.websocket_responses:
                                self.websocket_responses[int(var["id"])] = var
                            if var["event"] in self.main_subscriptions:
                                for function in self.main_subscriptions[var["event"]]:
                                    asyncio.create_task(function(var))
                        if self.debug:
                            print(Fore.GREEN + f"[RECEIVED] (main websocket)< {var}", end=Style.RESET_ALL + "\n")
                        if datetime.now() >= self.expire_time and create:
                            await self.ws_send({"id": self.increment(), "method": "GET", "path": "migrate", "authorization": f"{self.ws_headers['Authorization']}"})
                            create = False
                            self.migrate = True
                            await self.request_temp_token()
                            #print("migrating...")
                            asyncio.create_task(self.run_ws())
                    except websockets.ConnectionClosedOK:
                        #print("old websocket expired.")
                        return
                    except Exception:
                        traceback.print_exc()
                        print(Fore.RED + "There was an error in the main websocket. See above. I will try to start it again in 1 minute", end=Style.RESET_ALL + "\n")
                        await asyncio.sleep(60)
                        asyncio.create_task(self.run_ws())
                        return
        except asyncio.TimeoutError:
            print(Fore.RED + "Main websocket timeout (Is your connection working?) restarting in one minute...", end=Style.RESET_ALL + "\n")
            await asyncio.sleep(60)
            asyncio.create_task(self.run_ws())
            return

    def config(self, client_id, client_secret, scope_string, user_id, debug=False):
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

    async def ping_websocket(self):  # Function to periodically ping the websocket to keep connection alive.
        try:
            while not self.cred_initialized:
                await asyncio.sleep(1)
            while self.cred_initialized:
                await asyncio.sleep(10)
                await self.ws_send("ping!")  # Sends ping, it's an invalid command, but keeps the connection alive.
                await asyncio.sleep(4 * 60)  # Wait 4 minutes
        except Exception:
            print("ping_websocket failed. Restarting it in 1 minute...")
            await asyncio.sleep(60)
            await self.ping_websocket()

    async def wait_for_ready(self):
        while not self.cred_initialized:
            await asyncio.sleep(1)

    async def wait_for_ws(self):
        while not self.ws_connected:
            await asyncio.sleep(1)

    async def run(self):
        try:
            asyncio.create_task(self.run_ws())
        except:
            traceback.print_exc()
            print(Fore.RED + "Failed at task create_task() in Py_tale.", end=Style.RESET_ALL + "\n")
            exit()

        try:
            asyncio.create_task(self.request_temp_token())
        except:
            traceback.print_exc()
            print(Fore.RED + "Failed at task request_temp_token() in Py_tale.", end=Style.RESET_ALL + "\n")
            exit()

        await self.wait_for_ws()
        try:
            await self.ping_websocket()
        except:
            traceback.print_exc()
            print(Fore.RED + "Failed at task ping_websocket() in Py_tale.", end=Style.RESET_ALL + "\n")
            exit()
