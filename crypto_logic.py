# этот файл пока никак не влияет на проект, но в будущем все перенесется в такие файлы

# -*- coding: utf-8 -*-
import base64
import json
import os
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoEngine:
    def __init__(self, master_pass):
        self.master_pass = master_pass
        self.salt = self.get_or_create_salt()  # !проверяем соль
        self.cipher = self.generate_key()  # !генерируем ключ

    def get_or_create_salt(self):
        if not os.path.exists('salt.bin'):
            salt = os.urandom(16)
            with open('salt.bin', 'wb') as f:
                f.write(salt)
            return salt
        else:
            with open('salt.bin', 'rb') as f:
                return f.read()

    def generate_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_pass.encode()))
        return Fernet(key)

    def load_file(self):
        if not os.path.exists('data.json'):
            return []
        try:
            with open('data.json', 'rb') as f:
                encr_data = f.read()
                # дешифруем через наш собственный cipher
                decr_data = self.cipher.decrypt(encr_data).decode()
                return json.loads(decr_data)
        except Exception:
            return None  # если !ошибка расшифровки

    def write_to_file(self, data):
        json_str = json.dumps(data, ensure_ascii=False, indent=4)
        encr_data = self.cipher.encrypt(json_str.encode())
        try:
            with open('data.json', 'wb') as f:
                f.write(encr_data)
            print("Saved!")
            return True
        except IOError:
            print("Error saving!")
            return False


