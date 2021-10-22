import subprocess
import getpass
import json
import logging

import paramiko

from pathlib import Path

cmds = {
    '1': {
        "repr": "Show servers",
        "method": "_show_servers"
    },
    '2': {
        "repr": "Spawn shell",
        "method": "_spawn_shell"
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

        self._servers: list[dict] = self._load_servers(self._servers_p)
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

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
        client = self._client
        passphrase: str = None

        if self._is_encrypted:
            logging.info(f"Get passphrase of the f{self._key_p}")
            passphrase = getpass.getpass(f"Passphrase for the private key: ")

        logging.info(f"Try to connect to {host}:{port}")

        try:
            client.connect(hostname=host, port=port,
                           username=self._user, key_filename=str(self._key_p), passphrase=passphrase)
        except Exception as e:
            print(
                f"Connect to {host}:{port} has been failed.\n"
                f"Recommend to check whether private key requires passphrase.\n"
                f"If you want to get more detail log, run with '--debug'"
            )
            return False

        logging.info(f"Connection to {host}:{port} has been established.")
        return True

    def _spawn_shell(self) -> None:
        self._show_servers()
        idx = int(input("Idx > "))-1

        server = self._servers[idx]
        self._connect(server["host"], server["port"])

    def _show_servers(self) -> None:
        for idx, srv in enumerate(self._servers):
            print(f"[{idx+1}] {srv['name']}")
            print(f"Host: {srv['host']}")
            print(f"Port: {srv['port']}")
            print(f"Alive: {'O' if self._health_check(srv['host']) else 'X'}")
            print()

    def _quit(self) -> None:
        self._client.close()

        print("Bye!")
        quit()

    def interacitve(self):
        self._menu()
