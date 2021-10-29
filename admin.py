import subprocess
import getpass
import json
import logging
import signal
import paramiko

from pathlib import Path

from paramiko.client import SSHClient

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
        "repr": "Quit",
        "method": "_quit"
    }
}


class Admin:
    def __init__(self, user: str, key_p: Path, servers_p: Path, is_encrypted: bool = False) -> None:
        self._user: str = user
        self._key_p: Path = key_p
        self._servers_p: Path = servers_p

        self._is_encrypted: bool = is_encrypted
        self._passphrase: str = None

        self._servers: list[dict] = self._load_servers(self._servers_p)
        self._clients: dict = {}
        self._sudo_pw: str = None

        signal.signal(signal.SIGINT, self._quit)

    def _load_servers(self, servers_p: Path) -> list[dict[str:str]]:
        with open(servers_p) as servers_f:
            servers = json.load(servers_f)
            servers = [servers[name] | {'name': name}
                       for name in sorted(servers.keys())]
        return servers

    def _menu(self) -> None:
        while True:
            print(f"{'[menu]':=^30}")
            for cmd_idx in sorted(cmds.keys()):
                print(f"{cmd_idx}. {cmds[cmd_idx]['repr']}")
            print()
            selected: str = input("Select > ")
            print()

            if cmds[selected]['method'] != '_quit':
                print(f"{'['+cmds[selected]['repr']+']':=^30}")

            method: function = getattr(self, cmds[selected]["method"])

            method()

    def _health_check(self, host: str):
        try:
            subprocess.check_output(f"ping -c 1 {host}".split())
            return True
        except subprocess.CalledProcessError as grepexc:
            return False

    def _connect(self, host: str, port: int) -> bool:
        if self._has_connection(host):    # connection already exists
            logging.debug(f"connection already exists. return quick.")
            return True

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        passphrase: str = None

        # private is encrpyted with user passphrase
        if self._is_encrypted and not self._passphrase:
            logging.debug(f"Get passphrase of the {self._key_p}")
            passphrase = getpass.getpass(f"Passphrase for the private key: ")
            self._passphrase = passphrase

        logging.debug(f"Try to connect to {host}:{port}")
        try:
            client.connect(hostname=host, port=port,
                           username=self._user, key_filename=str(self._key_p), passphrase=self._passphrase)
        except Exception as e:
            logging.debug("connect has been failed.")
            print(
                f"Connect to {host}:{port} has been failed.\n"
                f"Recommend to check whether private key requires passphrase.\n"
                f"If you want to get more detail log, run with '--debug'"
            )
            return False

        logging.debug(f"Connection to {host}:{port} has been established.")
        self._clients.update({host: client})
        return True

    def _has_connection(self, host: str) -> bool:
        return host in self._clients.keys()

    def _show_servers(self) -> None:
        for idx, srv in enumerate(self._servers):
            print(f"[{idx+1}] {srv['name']}")
            print(f"Host: {srv['host']}")
            print(f"Port: {srv['port']}")
            print(f"Alive: {'O' if self._health_check(srv['host']) else 'X'}")
            print()

    def _add_user_to_server(self, uname: str, upw: str, server_idx: int) -> bool:
        server = self._servers[server_idx]
        host: str = server["host"]
        port: int = server["port"]

        if not self._connect(host, port):
            print(f"Failed to connect to {host}:{port}")
            return False

        client: paramiko.SSHClient = self._clients[host]
        cmd = f"sudo -S useradd -m -s /bin/bash -p {upw} {uname}"
        stdin, stdout, stderr = client.exec_command(cmd)

        # [TODO] Error handling
        if not self._sudo_pw:
            sudo_pw = getpass.getpass(f"Sudo password: ")
            stdin.write(sudo_pw)
            stdin.flush()
            self._sudo_pw = sudo_pw
        else:
            stdin.write(self._sudo_pw)
            stdin.flush()

        stdin.close()
        print(f"Succeed to add user `{uname}` @ {host}")
        return True

    def _add_user_to_servers(self) -> None:
        user_name = input("User name: ")
        user_pw = getpass.getpass("User password: ")

        print("\n- Servers")
        self._show_servers()
        idxs = [
            int(idx)-1 for idx in input("to which servers? (e.g. 1 2 3) > ").split()]

        for idx in idxs:
            self._add_user_to_server(user_name, user_pw, idx)

    def _quit(self, signal=None, frame=None) -> None:
        for _, conn in self._clients.items():
            conn.close()

        print("Bye!")
        quit()

    def interacitve(self):
        self._menu()
