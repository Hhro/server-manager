#!/usr/bin/env python3
import argparse
import getpass
import signal
import logging

from lib import Admin
from lib import AM
from lib import print_title

cmds = {
    '1': {
        "repr": "Login",
        "method": "_login"
    },
    "2": {
        "repr": "Register",
        "method": "_register"
    },
    '3': {
        "repr": "Quit",
        "method": "_quit"
    }
}


class ServerManager:
    def __init__(self):
        signal.signal(signal.SIGINT, self._quit)

    def _login(self) -> bool:
        username = input("Enter username: ")
        secret = getpass.getpass("Enter password: ")
        admin = Admin(username, secret)
        is_valid = admin.login()

        if not is_valid:
            print("Login has failed!")
            return False
        else:
            print("Login success!")
            admin.menu()

    def _register(self):
        username: str = input("Enter username: ")
        secret: str = getpass.getpass("Enter secret: ")
        AM.register(username, secret)

        print("Register success!")

    def _quit(self, signal=None, frame=None) -> None:
        print("Bye!")
        quit()

    def _menu(self):
        while True:
            print_title("Server Manager")
            for cmd_idx in sorted(cmds.keys()):
                print(f"{cmd_idx}. {cmds[cmd_idx]['repr']}")
            print()
            selected: str = input("Select > ")

            if cmds[selected]['method'] != '_quit':
                print_title(cmds[selected]['repr'])

            method: function = getattr(self, cmds[selected]["method"])

            method()

    def run(self):
        self._menu()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--debug", action="store_true", default=False, help="print debug messages"
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("paramiko").setLevel(logging.DEBUG)

    ServerManager().run()
