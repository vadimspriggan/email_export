import os
import imapclient
import email
from utils import sanitize_filename, save_attachments, verify_and_retry, clean_up

def get_folder_selection(mail):
    print("Получение списка всех папок...")
    # Получение списка всех папок
    folders = mail.list_folders()
    if not folders:
        print("Не удалось получить список папок")
        mail.logout()
        return None, None

    # Вывод списка папок с индексами
    print("Список папок:")
    for i, folder in enumerate(folders):
        print(f"{i:02d} - {folder[2]}")

    selected_folders = input("Какие папки вы бы хотели включить в выгрузку? (a - для всех, или укажите индексы через запятую): ")
    if selected_folders.strip().lower() == 'a':
        return 'a', folders
    else:
        selected_folders = [int(i) for i in selected_folders.split(",")]
        return selected_folders, folders

def process_account(imap_server, email_account, email_password, save_path, save_option, verify_option, delete_option, selected_folders):
    print(f"Обработка учетной записи: {email_account}")

    print("Подключение к серверу IMAP...")
    # Подключение к серверу IMAP
    mail = imapclient.IMAPClient(imap_server, ssl=True)
    mail.login(email_account, email_password)
    print("Успешное подключение")

    if selected_folders == 'a':
        folders = mail.list_folders()
        selected_folders = list(range(len(folders)))
    else:
        folders = mail.list_folders()

    # Создание папок для сохранения писем и вложений, если это необходимо
    if save_option in [1, 3]:
        os.makedirs(os.path.join(save_path, 'emails'), exist_ok=True)
    if save_option in [2, 3]:
        os.makedirs(os.path.join(save_path, 'attachments'), exist_ok=True)

    # Обработка выбранных папок
    for i in selected_folders:
        flags, delimiter, folder_name = folders[i]
        sanitized_folder_name = sanitize_filename(folder_name)
        print(f"Обработка папки: {folder_name}")

        # Выбор папки
        try:
            mail.select_folder(folder_name)

            # Поиск всех писем в папке
            messages = mail.search('ALL')
            if not messages:
                print(f"Нет писем в папке {folder_name}")
                continue

            print(f"Найдено {len(messages)} писем в папке {folder_name}")

            # Скачивание и сохранение каждого письма и вложений
            for email_id in messages:
                msg_data = mail.fetch([email_id], ['RFC822'])
                raw_email = msg_data[email_id][b'RFC822']
                msg = email.message_from_bytes(raw_email)

                if save_option in [1, 3]:
                    # Сохранение письма в формате .eml
                    email_folder_path = os.path.join(save_path, 'emails', sanitized_folder_name)
                    os.makedirs(email_folder_path, exist_ok=True)
                    email_file_path = os.path.join(email_folder_path, f'{email_id}.eml')
                    with open(email_file_path, 'wb') as f:
                        f.write(raw_email)

                    if verify_option:
                        if not verify_and_retry(email_file_path, raw_email):
                            print(f"Повторная проверка контрольной суммы не удалась для письма {email_id} в папке {folder_name}")
                        else:
                            print(f"Письмо {email_id} успешно проверено и сохранено в папке {email_folder_path}")
                            if delete_option:
                                mail.delete_messages(email_id)
                                mail.expunge()
                                print(f"Письмо {email_id} удалено с сервера")
                    else:
                        print(f"Письмо {email_id} сохранено в папке {email_folder_path}")

                if save_option in [2, 3]:
                    # Сохранение вложений
                    attachments_folder_path = os.path.join(save_path, 'attachments', sanitized_folder_name, str(email_id))
                    os.makedirs(attachments_folder_path, exist_ok=True)
                    save_attachments(msg, email_id, attachments_folder_path)

        except Exception as e:
            print(f"Ошибка при обработке папки {folder_name}: {e}")

    # Удаление вспомогательных файлов
    for root, _, files in os.walk(save_path):
        for file in files:
            if file.endswith('.md5'):
                os.remove(os.path.join(root, file))

    mail.logout()
    print("Обработка завершена")
