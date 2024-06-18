import re
import os
import hashlib
from collections import Counter

def sanitize_filename(filename):
    """Удаление или замена недопустимых символов в именах файлов"""
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    filename = re.sub(r'\s+', "_", filename)
    return filename

def save_attachments(msg, email_id, folder_path):
    """Сохранение вложений"""
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if filename:
            sanitized_filename = sanitize_filename(filename)
            filepath = os.path.join(folder_path, sanitized_filename)
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
    print(f"Вложения для письма {email_id} сохранены в папке {folder_path}")

def calculate_checksum(content):
    """Вычисление контрольной суммы MD5"""
    hash_md5 = hashlib.md5()
    hash_md5.update(content)
    return hash_md5.hexdigest()

def verify_and_retry(file_path, raw_email, retries=3):
    """Проверка контрольной суммы и повторная проверка при ошибке"""
    original_checksum = calculate_checksum(raw_email)
    checksums = [original_checksum]

    for attempt in range(retries):
        with open(file_path, 'rb') as f:
            saved_email = f.read()
        saved_checksum = calculate_checksum(saved_email)
        checksums.append(saved_checksum)
        if original_checksum == saved_checksum:
            return True
        else:
            print(f"Попытка {attempt + 1} проверки контрольной суммы не удалась для файла {file_path}")

    # Проверка контрольных сумм на большинство совпадений
    most_common_checksum, count = Counter(checksums).most_common(1)[0]
    if count > 1:
        # Перезапись файла с наиболее частой контрольной суммой
        with open(file_path, 'wb') as f:
            f.write(raw_email)
        return True
    else:
        return False

def clean_up(file_path):
    """Удаление файла и его контрольной суммы"""
    os.remove(file_path)
    checksum_file = f"{file_path}.md5"
    if os.path.exists(checksum_file):
        os.remove(checksum_file)
