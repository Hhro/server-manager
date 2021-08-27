#!/usr/bin/env python3
import argparse
import getpass
from pathlib import Path

import admin

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--user", required=True,
                        help="username of the admin")
    parser.add_argument("-i", "--key", required=True,
                        help="path of the admin private key")
    parser.add_argument("-p", "--phrase", action="store_true",
                        help="passphrase is required")
    parser.add_argument(
        "-s", "--servers", default="./servers.json", help="path of the servers.json")

    args = parser.parse_args()

    user = args.user

    # Private key
    key_p = Path(args.key)

    if not key_p.exists():
        raise FileNotFoundError(f"{key_p} not found")

    if args.phrase:
        phrase = getpass.getpass("Passphrase: ")

    # Server
    servers_p = Path(args.servers)

    if not servers_p.exists():
        raise FileNotFoundError(f"{servers_p} not found")

    master = admin.Admin(user, key_p, servers_p)
    master.interacitve()
