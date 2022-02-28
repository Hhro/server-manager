import subprocess
import logging
import paramiko
import signal
import getpass

from pathlib import Path

from .utils import mk_shadow
from .account import AM
from .resource import RM

cmds = {
    '1': {
        "repr": "Show servers",
        "method": "_show_servers"
    },
    '2': {
        "repr": "Add user",
        "method": "_add_user_to_servers"
    },
    '3': {
        "repr": "Upload file",
        "method": "_upload_file_to_servers"
    },
    '4': {
        "repr": "Add server credential",
        "method": "_add_cred"
    },
    '5': {
        "repr": "Quit",
        "method": "_quit"
    }
}


class Admin:
    def __init__(self, uname, secret):
        self._uname = uname
        self._secret = secret
        self._creds = {}
        self._sorted_creds = []
        self._clients = {}
        signal.signal(signal.SIGINT, self._quit)

    def _has_connection(self, host: str) -> bool:
        return host in self._clients.keys()

    def _health_check(self, host: str):
        try:
            subprocess.check_output(f"ping -c 1 {host}".split())
            return True
        except subprocess.CalledProcessError as grepexc:
            return False

    def _connect(self, cname: str) -> bool:

        if self._has_connection(cname):    # connection already exists
            return True

        cred = self._creds[cname]

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        user = cred["user"]
        host = cred["host"]
        port = int(cred["port"])
        priv_key = cred["priv_key"]
        passphrase = None
        # private key is encrpyted with user passphrase
        if cred["is_encrypted"]:
            passphrase = cred["passphrase"]

        logging.debug(f"Try to connect to {user}@{host}:{port}")
        try:
            client.connect(hostname=host, port=port,
                           username=user, key_filename=priv_key, passphrase=passphrase)
        except Exception as e:
            logging.debug("connect has been failed.")
            return False

        logging.debug(f"Connection to {host}:{port} has been established.")
        self._clients.update({cname: client})
        return True

    def _show_servers(self) -> None:
        for idx, (name, cred) in enumerate(self._sorted_creds):
            print(f"[{idx+1}] {name}")
            print(f"Host: {cred['host']}")
            print(f"Port: {cred['port']}")
            print(f"Alive: {'O' if self._health_check(cred['host']) else 'X'}")
            print()

    def _add_user_to_server(self, uname: str, shadow: str, server_idx: int) -> bool:
        cname, cred = self._sorted_creds[server_idx]
        if not self._connect(cname):
            return False

        client: paramiko.SSHClient = self._clients[cname]
        cmd = f"sudo -S useradd -m -s /bin/bash {uname} -p '{shadow}'"
        stdin, _, _ = client.exec_command(cmd)

        # [TODO] Error handling
        sudo_pw = cred["sudo_pw"]
        stdin.write(sudo_pw)
        stdin.flush()
        stdin.close()

        print(f"Succeed to add user `{uname}` @ {cname}")
        return True

    def _add_user_to_servers(self) -> None:
        user_name = input("User name: ")
        user_pw = getpass.getpass("User password: ")
        shadow = mk_shadow(user_pw)

        print("\n- Servers")
        self._show_servers()
        idxs = [
            int(idx)-1 for idx in input("to which servers? (e.g. 1 2 3) > ").split()]

        for idx in idxs:
            self._add_user_to_server(user_name, shadow, idx)

    def _add_cred_manual(self):
        name = input("Server name: ")

        host = input("Host: ")
        port = input("Port(default=22): ")
        if port == "":
            port = str(22)

        uname = input(f"User name(default={self._uname}): ")
        if uname == "":
            uname = self._uname
        sudo_pw = getpass.getpass("sudo password: ")

        priv_key = str(Path(input("Private key file path: ")).expanduser())
        is_encrypted = input("Is private key encrypted(y/n): ") == "y"
        passphrase = ""
        if is_encrypted:
            passphrase = getpass.getpass("passphrase: ")

        self._creds.update({name: {
            "host": host,
            "port": port,
            "user": uname,
            "priv_key": priv_key,
            "is_encrypted": is_encrypted,
            "passphrase": passphrase,
            "sudo_pw": sudo_pw
        }})
        AM.write_creds(self._uname, self._creds, self._secret)
        self._sorted_creds = sorted(self._creds.items())

    def _load_creds_from_csv(self):
        RM.list_creds()
        cred_idx = int(input("Select csv file: "))
        creds = RM.load_creds(cred_idx)

        RM.list_keys()
        priv_idx = int(input("Select private key: "))
        priv_p = RM.get_priv_p(priv_idx)

        sudo_pw = getpass.getpass("sudo password (blank if not required): ")
        passphrase = getpass.getpass("passphrase (blank if not required): ")
        is_encrypted = not (passphrase == "")

        for (name, srv_info) in creds.items():
            host = srv_info["Host"]
            uname = srv_info["Username"]
            self._creds.update({f"{name}": {
                "host": host,
                "port": 22,
                "user": uname,
                "priv_key": str(priv_p),
                "is_encrypted": is_encrypted,
                "passphrase": passphrase,
                "sudo_pw": sudo_pw,
            }})
        AM.write_creds(self._uname, self._creds, self._secret)
        self._sorted_creds = sorted(self._creds.items())

    def _add_cred(self):
        print("1. Manually add credential")
        print("2. Load from csv")
        select = input("Select > ")

        if select == '1':
            self._add_cred_manual()
        elif select == '2':
            self._load_creds_from_csv()

    def _upload_file(self, server_idx: int, local: str, remote: str) -> bool:
        cname, cred = self._sorted_creds[server_idx]
        if not self._connect(cname):
            return False

        client: paramiko.SSHClient = self._clients[cname]
        sftp_client = client.open_sftp()
        sftp_client.put(local, remote)
        sftp_client.close()

        print(f"Upload success: {local} -> {cred['host']}:{remote}")

        return True

    def _upload_file_to_servers(self) -> None:
        print("\n- Servers")
        self._show_servers()
        idxs = [
            int(idx)-1 for idx in input("to which servers? (e.g. 1 2 3) > ").split()]

        print("\n- Local file")
        local = str(Path(input("Path: ")).expanduser())

        print("\n- Remote path")
        remote = input("Path: ")

        for idx in idxs:
            self._upload_file(idx, local, remote)

    def _quit(self, signal=None, frame=None) -> None:
        for _, conn in self._clients.items():
            conn.close()

        print("Bye!")
        quit()

    def login(self) -> bool:
        creds = AM.creds_of(self._uname, self._secret)
        print(creds)

        if creds == False:
            return False
        else:
            self._creds = creds
            self._sorted_creds = sorted(self._creds.items())
            return True

    def menu(self):
        while True:
            print(f"{'[menu of '+f'{self._uname}]':=^30}")
            for cmd_idx in sorted(cmds.keys()):
                print(f"{cmd_idx}. {cmds[cmd_idx]['repr']}")
            print()
            selected: str = input("Select > ")
            print()

            if cmds[selected]['method'] != '_quit':
                print(f"{'['+cmds[selected]['repr']+']':=^30}")

            method: function = getattr(self, cmds[selected]["method"])

            method()
