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
    print(f"Сейчас в конфигурационном файле {len(config['accounts'])} серверов")
    for i, account in enumerate(config['accounts']):
        print(f"{i:02d} - Сервер: {account['IMAP_SERVER']}")
        print(f"     Логин: {account['EMAIL_ACCOUNT']}")
        print(f"     Пароль: {account['EMAIL_PASSWORD']}")
    print()

def add_server(config):
    print("Добавление нового сервера")
    server = input("Адрес сервера: ")
    login = input("Логин: ")
    password = input("Пароль: ")
    config['accounts'].append({
        'IMAP_SERVER': server,
        'EMAIL_ACCOUNT': login,
        'EMAIL_PASSWORD': password
    })
    save_config(config)
    index = len(config['accounts']) - 1
    print(f"Запись сохранена в индексе {index:02d}")
    print()

def edit_server(config):
    index = input("Введите индекс сервера для редактирования: ")
    try:
        index = int(index)
        account = config['accounts'][index]
    except (ValueError, IndexError):
        print("Нет такого сервера")
        return
    print("Оставьте поле пустым, чтобы сохранить текущее значение.")
    server = input(f"Адрес сервера ({account['IMAP_SERVER']}): ") or account['IMAP_SERVER']
    login = input(f"Логин ({account['EMAIL_ACCOUNT']}): ") or account['EMAIL_ACCOUNT']
    password = input(f"Пароль ({account['EMAIL_PASSWORD']}): ") or account['EMAIL_PASSWORD']
    account.update({
        'IMAP_SERVER': server,
        'EMAIL_ACCOUNT': login,
        'EMAIL_PASSWORD': password
    })
    save_config(config)
    print(f"Запись сохранена в индексе {index:02d}")
    print()

def delete_server(config):
    index = input("Введите индекс сервера для удаления (или 'a' для всех): ")
    if index.strip().lower() == 'a':
        config['accounts'] = []
    else:
        try:
            index = int(index)
            del config['accounts'][index]
        except (ValueError, IndexError):
            print("Нет такого сервера")
            return
    save_config(config)
    print("Сервер(а) удален(ы)")
    print()

def main():
    config = load_config()
    while True:
        print(f"Сейчас в конфигурационном файле {len(config['accounts'])} серверов")
        action = input("Что вы хотите?\nl - посмотреть их\nn - добавить новый\ne - отредактировать имеющийся\nd - удалить\nq - выход\n").strip().lower()
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
            print("Неизвестное действие, попробуйте снова.")

if __name__ == "__main__":
    main()
