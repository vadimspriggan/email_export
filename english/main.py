import os
import imapclient
import subprocess
from config import load_config
from imap_handler import get_folder_selection, process_account
from utils import sanitize_filename

def main():
    # Configuration check
    config = load_config()
    num_servers = len(config['accounts'])
    print(f"There are currently {num_servers} servers in the configuration file")
    change_config = input("Do you want to edit the configuration file? (y/N): ").strip().lower()
    
    if change_config == 'y':
        # Run make_config.py
        subprocess.run(["python", "make_config.py"])
        # Reload configuration after make_config completion
        config = load_config()
    
    # Select save option
    while True:
        print("Select save option:")
        print("1 - Save only .eml files")
        print("2 - Save only attachments")
        print("3 - Save both .eml files and attachments")
        save_option_input = input("Enter option number (1, 2, or 3): ").strip()
        if save_option_input in ['1', '2', '3']:
            SAVE_OPTION = int(save_option_input)
            break
        else:
            print("You did not enter anything or entered an incorrect value. Please try again.")

    # Request path for saving export
    save_path = input("Enter the full path for saving the export (leave empty to place in the parent folder of the current one): ")
    if not save_path:
        save_path = os.path.dirname(os.getcwd())

    # Request to enable export verification
    verify_option = input("Do you want to enable export verification? This will take longer with a large number of emails and increase internet traffic usage. (Y/n): ").strip().lower() != 'n'

    # Request to delete verified emails if verification and option 1 or 3 are selected
    delete_option = False
    if verify_option and SAVE_OPTION in [1, 3]:
        delete_option = input("Do you want to delete verified emails? (y/N): ").strip().lower() == 'y'

    # Connect to the first account to get the list of folders
    first_account = config['accounts'][0]
    mail = imapclient.IMAPClient(first_account['IMAP_SERVER'], ssl=True)
    mail.login(first_account['EMAIL_ACCOUNT'], first_account['EMAIL_PASSWORD'])
    selected_folders, folders = get_folder_selection(mail)
    mail.logout()

    # Process all accounts from the configuration file
    for account in config['accounts']:
        imap_server = account['IMAP_SERVER']
        email_account = account['EMAIL_ACCOUNT']
        email_password = account['EMAIL_PASSWORD']

        # Create the main export folder named after EMAIL_ACCOUNT
        account_save_path = os.path.join(save_path, sanitize_filename(email_account))
        os.makedirs(account_save_path, exist_ok=True)

        # Process current account
        process_account(imap_server, email_account, email_password, account_save_path, SAVE_OPTION, verify_option, delete_option, selected_folders)

if __name__ == '__main__':
    try:
        main()
    except imapclient.exceptions.IMAPClientError as e:
        print(f"IMAP error: {e}")
    except Exception as e:
        print(f"General error: {e}")
