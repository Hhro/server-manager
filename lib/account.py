#!/usr/bin/env python3
import os
import json
import base64

from pathlib import Path
from Crypto.Cipher import AES
from hashlib import sha256

ACC_P = (Path(__file__).parent.parent) / "rsrc" / "accounts.json"


class Cipher:
    def __init__(self, secret: bytes):
        self._bs = AES.block_size
        self._key = sha256(secret).digest()

    def _pad(self, s: bytes) -> bytes:
        s = bytearray(s)
        return bytes(s + (self._bs - len(s) % self._bs) * chr(self._bs - len(s) % self._bs).encode())

    def _unpad(self, s: bytes) -> bytes:
        return s[:-s[len(s)-1]]

    def encrypt(self, data: bytes) -> bytes:
        data = self._pad(data)
        iv = os.urandom(self._bs)
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(data))

    def decrypt(self, enc: bytes) -> bytes:
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))


class AccountManager:
    def __init__(self, acc_p: Path = ACC_P):
        if not acc_p.exists():
            acc_p.touch()
            acc_p.write_text("{}")

        self._acc_p = acc_p
        self._accounts: dict = json.loads(acc_p.read_text())

    def _is_exist(self, uname: str):
        return uname in self._accounts

    def register(self, uname: str, secret: str):
        encryptor = Cipher(secret.encode())
        self._accounts[uname] = encryptor.encrypt("{}".encode()).decode()
        self._acc_p.write_text(json.dumps(self._accounts))

    def creds_of(self, uname: str, secret: str):
        if not self._is_exist(uname):
            return False

        decryptor = Cipher(secret.encode())
        try:
            creds = json.loads(decryptor.decrypt(
                self._accounts[uname].encode()))
            return creds
        except:
            return False

    def write_creds(self, uname: str, creds: dict, secret: str):
        encryptor = Cipher(secret.encode())
        self._accounts[uname] = encryptor.encrypt(
            json.dumps(creds).encode()).decode()
        self._acc_p.write_text(json.dumps(self._accounts))


AM = AccountManager()
