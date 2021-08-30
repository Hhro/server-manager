#!/usr/bin/env python3
import argparse
import logging
import paramiko

import admin

from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--user", required=True,
                        help="username of the admin")
    parser.add_argument("-i", "--key", required=True,
                        help="path of the admin private key")
    parser.add_argument("-p", "--encrypted", action="store_true", default=False,
                        help="passphrase is required")
    parser.add_argument(
        "-s", "--servers", default="./servers.json", help="path of the servers.json")
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="verbose log messages"
    )
    parser.add_argument(
        "-V", "--debug", action="store_true", default=False, help="more verbose log messages"
    )

    args = parser.parse_args()

    # username
    user: str = args.user

    # private key
    key_p: Path = Path(args.key)

    if not key_p.exists():
        raise FileNotFoundError(f"{key_p} not found")

    # private key is encrypted with the passphrase
    is_encrypted: bool = args.encrypted

    # server information
    servers_p: Path = Path(args.servers)

    if not servers_p.exists():
        raise FileNotFoundError(f"{servers_p} not found")

    # logger
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
        paramiko.common.logging.basicConfig(level=logging.INFO)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)
        paramiko.common.logging.basicConfig(level=logging.DEBUG)

    master = admin.Admin(user, key_p, servers_p, is_encrypted)
    master.interacitve()
