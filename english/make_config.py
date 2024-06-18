import json
import os

CONFIG_FILE = 'config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {'accounts': []}
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

def list_servers(config):
    print(f"There are currently {len(config['accounts'])} servers in the configuration file")
    for i, account in enumerate(config['accounts']):
        print(f"{i:02d} - Server: {account['IMAP_SERVER']}")
        print(f"     Login: {account['EMAIL_ACCOUNT']}")
        print(f"     Password: {account['EMAIL_PASSWORD']}")
    print()

def add_server(config):
    print("Adding a new server")
    server = input("Server address: ")
    login = input("Login: ")
    password = input("Password: ")
    config['accounts'].append({
        'IMAP_SERVER': server,
        'EMAIL_ACCOUNT': login,
        'EMAIL_PASSWORD': password
    })
    save_config(config)
    index = len(config['accounts']) - 1
    print(f"Record saved at index {index:02d}")
    print()

def edit_server(config):
    index = input("Enter the server index to edit: ")
    try:
        index = int(index)
        account = config['accounts'][index]
    except (ValueError, IndexError):
        print("No such server")
        return
    print("Leave the field empty to keep the current value.")
    server = input(f"Server address ({account['IMAP_SERVER']}): ") or account['IMAP_SERVER']
    login = input(f"Login ({account['EMAIL_ACCOUNT']}): ") or account['EMAIL_ACCOUNT']
    password = input(f"Password ({account['EMAIL_PASSWORD']}): ") or account['EMAIL_PASSWORD']
    account.update({
        'IMAP_SERVER': server,
        'EMAIL_ACCOUNT': login,
        'EMAIL_PASSWORD': password
    })
    save_config(config)
    print(f"Record saved at index {index:02d}")
    print()

def delete_server(config):
    index = input("Enter the server index to delete (or 'a' for all): ")
    if index.strip().lower() == 'a':
        config['accounts'] = []
    else:
        try:
            index = int(index)
            del config['accounts'][index]
        except (ValueError, IndexError):
            print("No such server")
            return
    save_config(config)
    print("Server(s) deleted")
    print()

def main():
    config = load_config()
    while True:
        print(f"There are currently {len(config['accounts'])} servers in the configuration file")
        action = input("What would you like to do?\nl - list them\nn - add new\ne - edit existing\nd - delete\nq - quit\n").strip().lower()
        if action == 'l':
            list_servers(config)
        elif action == 'n':
            add_server(config)
        elif action == 'e':
            edit_server(config)
        elif action == 'd':
            delete_server(config)
        elif action == 'q':
            break
        else:
            print("Unknown action, please try again.")

if __name__ == "__main__":
    main()
