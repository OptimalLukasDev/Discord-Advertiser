import requests, json, time, os, websocket, threading, ssl, sys, select, datetime
from colorama import Fore, Back, Style

# Check for config & tokens
with open('config.json') as f:
    data = json.load(f)
token = data.get('token') or input("Enter your token: ").replace('"', '')
while requests.get('https://discord.com/api/v9/users/@me', headers={'Authorization': token}).status_code != 200:
    print("Invalid token")
    token = input("Enter your token: ")
data['token'] = token
message = data.get('message') or input("Enter your message: ")
delay = data.get('delay') or input("Enter your delay (in seconds): ")
channels = data.get('channels') or input("Enter channel ID/s (separated by a space): ").split(" ")
status = data.get('status')
while not status or status not in ("online", "idle", "dnd", "invisible"):
    status = input("Enter your status (online, idle, dnd, invisible): ")
    if status in ("online", "idle", "dnd", "invisible"):
        break
    else:
        print("Invalid status")
data['status'] = status
customStatus = data.get('customStatus') or input("Enter your custom status: ")
data['message'], data['delay'], data['channels'], data['customStatus'] = message, delay, channels, customStatus
with open('config.json', 'w') as f:
    json.dump(data, f)
    f.close()


# Actual advertiser
def sendMessage():
    start_time = time.time()
    print(Fore.RED + "Enter 'escape' to return to menu.")
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            if sys.stdin.readline().strip() == 'escape':
                break
        for channel in channels:
            requests.post(f'https://discord.com/api/v9/channels/{channel}/messages', headers={'Authorization': token}, json={'content': message})
            elapsed_time = time.time() - start_time
            elapsed_time_str = f"[{datetime.timedelta(seconds=elapsed_time)}s]"
            print(Fore.YELLOW + f"{elapsed_time_str} Sent message to channel {channel}")
        time.sleep(int(delay))

def modifyChannels(operation):
    channel = input("Enter channel ID: ")
    if operation == 'add':
        data['channels'].append(channel)
        update_config(data, 'channels')
    elif operation == 'remove':
        data['channels'].remove(channel)
        update_config(data, 'channels')
    time.sleep(3)

def changeMessage():
    data['message'] = input("Enter your message: ")
    update_config(data, 'message')

def changeDelay():
    data['delay'] = input("Enter your delay (in seconds): ")
    update_config(data, 'delay')

def changeStatus():
    while True:
        status = input("Enter your status (online, idle, dnd, invisible): ")
        if status in ("online", "idle", "dnd", "invisible"):
            data['status'] = status
            update_config(data, 'status')
            break
        else:
            print("Invalid status. Please try again.")

def changeCustomStatus():
    data['customStatus'] = input("Enter your custom status: ")
    update_config(data, 'customStatus')

def update_config(data, parameter):
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Changed {parameter} to {data[parameter]}")
    time.sleep(3)

# Loop onliner
def onlineLoop():
    while True:
        online() 
        time.sleep(30)  

# Actual onliner
def online():
    status = data.get('status')
    customStatus = data.get('customStatus')
    ws = websocket.WebSocket() 
    ws.connect('wss://gateway.discord.gg/?v=9&encoding=json')
    cool = json.loads(ws.recv())
    heartbeat = cool['d']['heartbeat_interval']
    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Windows 11",
                "$browser": "Mozilla Firefox",
                "$device": "Windows",
            },
            "presence": {"status": status, "afk": False},
        },
        "s": None,
        "t": None,
    }
    ws.send(json.dumps(auth))
    yes = {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [
                {
                    "type": 4,
                    "state": customStatus,
                    "name": "Custom Status",
                    "id": "custom"
                }
            ],
            "status": status,
            "afk": False,
        }}
    def send_heartbeat():
        while True:
            try:
                ws.send(json.dumps(yes))
            except ssl.SSLEOFError:
                continue
            time.sleep(heartbeat / 1000)

    
    thread = threading.Thread(target=send_heartbeat)
    thread.start()
    

# Clear console
def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')

# Advertiser menu
def advertiser():
    while True:
        clearConsole()
        choice = input(Fore.RED+"Advertiser:\n"+Fore.YELLOW+"1. Start advertiser\n2. Add channel\n3. Remove channel\n4. Change message\n5. Change delay\n6. Leave\n")
        if choice == "1":
            clearConsole()
            sendMessage()
        elif choice == "2":
            modifyChannels('add')
        elif choice == "3":
            modifyChannels('remove')
        elif choice == "4":
            changeMessage()
        elif choice == "5":
            changeDelay()
        elif choice == "6":
            break
        else:
            print("Invalid choice")
            time.sleep(3)

# Onliner menu
def onliner():
    while True:
        clearConsole()
        choice = input(Fore.RED+"Onliner:\n"+Fore.YELLOW+"1. Start onliner\n2. Change status\n3. Change custom status\n4. Leave\n")
        if choice == "1":
            thread = threading.Thread(target=onlineLoop)
            thread.start()
            print("Started onliner")
        elif choice == "2":
            changeStatus()
        elif choice == "3":
            changeCustomStatus()
        elif choice == "4":
            break
        else:
            print("Invalid choice")
        time.sleep(3)

# Main menu
def main():
    while True:
        clearConsole()
        choice = input(Fore.RED+"Home:\n"+Fore.YELLOW+"1. Advertiser\n2. Onliner\n3. Exit\n")
        if choice == "1":
            advertiser()
        elif choice == "2":
            onliner()
        elif choice == "3":
            exit()
        else:
            print("Invalid choice")
            time.sleep(3)
        
# Main loop
while True:
    main()

