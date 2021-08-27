import pathlib
import json
import logging
from pathlib import Path

cmds = {
    '1': {
        "repr": "Show servers",
        "method": "_show_servers"
    },
}


class Admin:
    def __init__(self, user: str, key_p: pathlib.PosixPath, servers_p: pathlib.PosixPath) -> None:
        self._user: str = user
        self._key_p: pathlib.PosixPath = key_p
        self._servers_p: pathlib.PosixPath = servers_p

        self._servers: list[dict] = self._load_servers(self._servers_p)
        self._client = paramiko.SSHClient()

    def _load_servers(self, servers_p: pathlib.PosixPath) -> list[dict[str:str]]:
        with open(servers_p) as servers_f:
            servers = json.load(servers_f)
            servers = [servers[name] | {'name': name}
                       for name in sorted(servers.keys())]
        return servers

    def _menu(self):
        print(f"{'[menu]':=^30}")
        for cmd_idx in sorted(cmds.keys()):
            print(f"{cmd_idx}. {cmds[cmd_idx]['repr']}")
        print()
        selected: str = input("Select > ")
        print()

        print(f"{'['+cmds[selected]['repr']+']':=^30}")
        method: function = getattr(self, cmds[selected]["method"])
        method()

    def interacitve(self):
        self._menu()

    def show_servers(self):
        for idx, srv_name in enumerate(sorted(self._servers.keys())):
            srv: dict = self._servers[srv_name]

    def _show_servers(self):
        for idx, srv in enumerate(self._servers):
            print(f"[{idx+1}] {srv['name']}")
            print(f"Host: {srv['host']}")
            print(f"Port: {srv['port']}")
            print()

    def interacitve(self):
        self._menu()

if __name__ == "__main__":
    Admin("3", "4", "servers.json").show_servers()
