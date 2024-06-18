
# Email Exporter
![Project Cover](./image.png)

This program is designed for quickly and easily extracting all emails or selected folders from any mail server that supports IMAP. The program supports exporting from an unlimited number of mailboxes specified in the configuration file.

## Features

- IMAP server support.
- Ability to select specific folders for export.
- Export verification using checksums.
- Option to delete exported emails from the server.
- Export all emails with attachments or only attachments.
- Convenient configurator for managing the configuration file.

## Installation

1. Clone the repository:
    ```bash
    git clone <URL>
    ```

2. Navigate to the project directory:
    ```bash
    cd mailexport
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Configurator

To configure the configuration file, use `make_config.py`.

#### Running the Configurator
```bash
python make_config.py
```

### Main Program

To run the main program, use `main.py`.

#### Running the Main Program
```bash
python main.py
```

### Operation Description

When `main.py` is launched, the program first checks the number of servers in the configuration file and offers to change it if necessary.

```plaintext
There are currently n servers in the configuration file
Do you want to change the configuration file? (y/N)
```

If the user selects `y`, `make_config.py` is launched to edit the configuration. After the configurator completes, the program continues with the updated configuration.

#### Save Options

The program offers to choose a save option:
1. Save only `.eml` files.
2. Save only attachments.
3. Save both `.eml` files and attachments.

#### Save Path

The user can specify a full path for saving the export. If no path is specified, folders will be created one level above the current directory.

#### Export Verification

By default, export verification is enabled, performed using checksums. For each email, an MD5 checksum is calculated and then verified after the email is saved. If the checksum does not match, the email is re-downloaded up to three times.

#### Deleting Verified Emails

If verification is enabled and option 1 or 3 is selected, the user is offered the option to delete verified emails from the server.

### Examples

#### Example Configuration File (`config.json`)

```json
{
    "accounts": [
        {
            "IMAP_SERVER": "imap.gmail.com",
            "EMAIL_ACCOUNT": "your_email@gmail.com",
            "EMAIL_PASSWORD": "your_password"
        },
        {
            "IMAP_SERVER": "imap.yandex.com",
            "EMAIL_ACCOUNT": "another_email@yandex.com",
            "EMAIL_PASSWORD": "another_password"
        }
    ]
}
```

### Project Structure

- `main.py`: Main script for running email export.
- `make_config.py`: Configurator for managing the configuration file.
- `config.py`: Module for loading and saving the configuration file.
- `imap_handler.py`: Module for working with IMAP servers.
- `utils.py`: Utility functions for processing emails and attachments.
- `config.json`: Configuration file with email server accounts.

### License

This project is licensed under the GPL-3.0 License.
