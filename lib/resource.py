#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

from .display import print_title

RESOURCES_DIR = (Path(__file__).parent.parent) / "rsrc"


class ResourceManager:
    def __init__(self, is_debug=True):
        self._resources_dir = RESOURCES_DIR
        self._scripts_dir = RESOURCES_DIR / "scripts"
        self._scripts_p = sorted(self._scripts_dir.glob("*"))
        self._keys_dir = RESOURCES_DIR / "keys"
        self._keys_p = sorted(self._keys_dir.glob("*"))
        self._creds_dir = RESOURCES_DIR / "creds"
        self._creds_p = sorted(self._creds_dir.glob("*"))

        if not self._resources_dir.exists():
            self._resources_dir.mkdir(exist_ok=True, parents=True)

        if not self._scripts_dir.exists():
            self._scripts_dir.mkdir(exist_ok=True, parents=True)

    def list_scripts(self) -> bool:
        print_title("Scripts")
        print(f"{'Idx':^7} | {'Name':^40}")
        print("-"*50)

        for idx, script in enumerate(self._scripts_p):
            print(f"{idx+1:^7} | {str(script.name)}")
        print()

    def list_keys(self) -> bool:
        print_title("Keys")
        print(f"{'Idx':^7} | {'Name':^40}")
        print("-"*50)

        for idx, key in enumerate(self._keys_p):
            print(f"{idx+1:^7} | {str(key.name)}")
        print()

    def list_creds(self) -> bool:
        print_title("Creds")
        print(f"{'Idx':^7} | {'Name':^40}")
        print("-"*50)

        for idx, cred in enumerate(self._creds_p):
            print(f"{idx+1:^7} | {str(cred.name)}")
        print()

    def load_creds(self, idx: int) -> dict:
        if idx < 1 or idx > len(self._creds_p):
            return None

        with open(self._creds_p[idx-1], "r") as f:
            creds = pd.read_csv(f, encoding="utf-8")
            if "Name" not in creds.columns:
                return None

            try:
                return creds.set_index("Name").T.to_dict()
            except:
                print("Name is not unique in creds file")
                return None

    def get_priv_p(self, idx: int) -> Path:
        if idx < 1 or idx > len(self._keys_p):
            return None

        return self._keys_p[idx-1]


RM = ResourceManager()

if __name__ == "__main__":
    RM.list_scripts()
