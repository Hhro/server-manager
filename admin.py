import pathlib
import json
import logging
from pathlib import Path

cmds = {
    '1': {
        "repr": "Show servers",
        "method": "show_servers"
    },
}


class Admin:
    def __init__(self, user: str, key_p: pathlib.PosixPath, servers_p: pathlib.PosixPath) -> None:
        self._user: str = user
        self._key_p: pathlib.PosixPath = key_p

        self._servers_p: pathlib.PosixPath = servers_p
        self._servers: dict = self._load_servers(self._servers_p)

    def _load_servers(self, servers_p: pathlib.PosixPath):
        with open(servers_p) as servers_f:
            servers: dict = json.load(servers_f)
        return servers

    def _menu(self):
        for cmd_idx in sorted(cmds.keys()):
            print(f"{cmd_idx}. {cmds[cmd_idx]['repr']}")
        selected: str = input("Select> ")

        method: function = getattr(self, cmds[selected]["method"])
        method()

    def interacitve(self):
        self._menu()

    def show_servers(self):
        for idx, srv_name in enumerate(sorted(self._servers.keys())):
            srv: dict = self._servers[srv_name]

            print(f"[{idx+1}] {srv_name}")
            print(f"Host: {srv['host']}")
            print(f"Port: {srv['port']}")
            print()


if __name__ == "__main__":
    Admin("3", "4", "servers.json").show_servers()
