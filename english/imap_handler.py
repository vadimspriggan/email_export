import os
import imapclient
import email
from utils import sanitize_filename, save_attachments, verify_and_retry, clean_up

def get_folder_selection(mail):
    print("Getting list of all folders...")
    # Getting list of all folders
    folders = mail.list_folders()
    if not folders:
        print("Failed to get the list of folders")
        mail.logout()
        return None, None

    # Displaying list of folders with indices
    print("List of folders:")
    for i, folder in enumerate(folders):
        print(f"{i:02d} - {folder[2]}")

    selected_folders = input("Which folders would you like to include in the export? (a - for all, or specify indices separated by commas): ")
    if selected_folders.strip().lower() == 'a':
        return 'a', folders
    else:
        selected_folders = [int(i) for i in selected_folders.split(",")]
        return selected_folders, folders

def process_account(imap_server, email_account, email_password, save_path, save_option, verify_option, delete_option, selected_folders):
    print(f"Processing account: {email_account}")

    print("Connecting to IMAP server...")
    # Connecting to IMAP server
    mail = imapclient.IMAPClient(imap_server, ssl=True)
    mail.login(email_account, email_password)
    print("Connection successful")

    if selected_folders == 'a':
        folders = mail.list_folders()
        selected_folders = list(range(len(folders)))
    else:
        folders = mail.list_folders()

    # Creating folders for saving emails and attachments if necessary
    if save_option in [1, 3]:
        os.makedirs(os.path.join(save_path, 'emails'), exist_ok=True)
    if save_option in [2, 3]:
        os.makedirs(os.path.join(save_path, 'attachments'), exist_ok=True)

    # Processing selected folders
    for i in selected_folders:
        flags, delimiter, folder_name = folders[i]
        sanitized_folder_name = sanitize_filename(folder_name)
        print(f"Processing folder: {folder_name}")

        # Selecting folder
        try:
            mail.select_folder(folder_name)

            # Searching for all emails in the folder
            messages = mail.search('ALL')
            if not messages:
                print(f"No emails in folder {folder_name}")
                continue

            print(f"Found {len(messages)} emails in folder {folder_name}")

            # Downloading and saving each email and attachment
            for email_id in messages:
                msg_data = mail.fetch([email_id], ['RFC822'])
                raw_email = msg_data[email_id][b'RFC822']
                msg = email.message_from_bytes(raw_email)

                if save_option in [1, 3]:
                    # Saving email as .eml
                    email_folder_path = os.path.join(save_path, 'emails', sanitized_folder_name)
                    os.makedirs(email_folder_path, exist_ok=True)
                    email_file_path = os.path.join(email_folder_path, f'{email_id}.eml')
                    with open(email_file_path, 'wb') as f:
                        f.write(raw_email)

                    if verify_option:
                        if not verify_and_retry(email_file_path, raw_email):
                            print(f"Retry checksum verification failed for email {email_id} in folder {folder_name}")
                        else:
                            print(f"Email {email_id} successfully verified and saved in folder {email_folder_path}")
                            if delete_option:
                                mail.delete_messages(email_id)
                                mail.expunge()
                                print(f"Email {email_id} deleted from server")
                    else:
                        print(f"Email {email_id} saved in folder {email_folder_path}")

                if save_option in [2, 3]:
                    # Saving attachments
                    attachments_folder_path = os.path.join(save_path, 'attachments', sanitized_folder_name, str(email_id))
                    os.makedirs(attachments_folder_path, exist_ok=True)
                    save_attachments(msg, email_id, attachments_folder_path)

        except Exception as e:
            print(f"Error processing folder {folder_name}: {e}")

    # Removing auxiliary files
    for root, _, files in os.walk(save_path):
        for file in files:
            if file.endswith('.md5'):
                os.remove(os.path.join(root, file))

    mail.logout()
    print("Processing completed")
