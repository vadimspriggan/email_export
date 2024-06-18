import os
import imapclient
import subprocess
from config import load_config
from imap_handler import get_folder_selection, process_account
from utils import sanitize_filename

def main():
    # Проверка конфигурации
    config = load_config()
    num_servers = len(config['accounts'])
    print(f"Сейчас в конфигурационном файле {num_servers} серверов")
    change_config = input("Хотите изменить конфигурационный файл? (y/N): ").strip().lower()
    
    if change_config == 'y':
        # Запуск make_config.py
        subprocess.run(["python", "make_config.py"])
        # Повторная загрузка конфигурации после завершения make_config
        config = load_config()
    
    # Выбор опции сохранения
    while True:
        print("Выберите опцию сохранения:")
        print("1 - Сохранение только .eml файлов")
        print("2 - Сохранение только вложений")
        print("3 - Сохранение и .eml файлов и вложений")
        save_option_input = input("Введите номер опции (1, 2 или 3): ").strip()
        if save_option_input in ['1', '2', '3']:
            SAVE_OPTION = int(save_option_input)
            break
        else:
            print("Вы ничего не ввели или ввели некорректное значение. Попробуйте снова.")

    # Запрос пути для сохранения выгрузки
    save_path = input("Введите полный путь для сохранения выгрузки (оставьте пустым для размещения в родительской папке текущей): ")
    if not save_path:
        save_path = os.path.dirname(os.getcwd())

    # Запрос включения проверки выгрузки
    verify_option = input("Хотите ли вы включить проверку выгрузки, это займёт больше времени при большом количестве писем и увеличит расход интернет-трафика? (Y/n): ").strip().lower() != 'n'

    # Запрос удаления проверенных писем, если выбрана проверка и опция 1 или 3
    delete_option = False
    if verify_option and SAVE_OPTION in [1, 3]:
        delete_option = input("Хотите ли вы удалять проверенные письма? (y/N): ").strip().lower() == 'y'

    # Подключение к первому аккаунту для получения списка папок
    first_account = config['accounts'][0]
    mail = imapclient.IMAPClient(first_account['IMAP_SERVER'], ssl=True)
    mail.login(first_account['EMAIL_ACCOUNT'], first_account['EMAIL_PASSWORD'])
    selected_folders, folders = get_folder_selection(mail)
    mail.logout()

    # Обработка всех учетных записок из конфигурационного файла
    for account in config['accounts']:
        imap_server = account['IMAP_SERVER']
        email_account = account['EMAIL_ACCOUNT']
        email_password = account['EMAIL_PASSWORD']

        # Создание основной папки для выгрузки по имени EMAIL_ACCOUNT
        account_save_path = os.path.join(save_path, sanitize_filename(email_account))
        os.makedirs(account_save_path, exist_ok=True)

        # Обработка текущего аккаунта
        process_account(imap_server, email_account, email_password, account_save_path, SAVE_OPTION, verify_option, delete_option, selected_folders)

if __name__ == '__main__':
    try:
        main()
    except imapclient.exceptions.IMAPClientError as e:
        print(f"Ошибка IMAP: {e}")
    except Exception as e:
        print(f"Общая ошибка: {e}")
