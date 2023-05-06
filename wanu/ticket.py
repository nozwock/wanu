import subprocess
import re
import os
from pathlib import Path
from dataclasses import dataclass
from wanu.defines import TITLEKEY_PATH, SWITCH_DIR


@dataclass
class TitleKey:
    rights_id: str
    title_key: str

    @staticmethod
    def new(tik_path: Path) -> TitleKey | None:
        tik_content = subprocess.run(
            ["xxd", tik_path], capture_output=True, text=True
        ).stdout
        title_match = re.search(r"(?<=2a0: ).{39}", tik_content)
        key_match = re.search(r"(?<=180: ).{39}", tik_content)

        if title_match and key_match:
            title = title_match.group(0).replace(" ", "")
            key = key_match.group(0).replace(" ", "")
            return TitleKey(title, key)
        return None


def store_title_key(keys: list[TitleKey]) -> None:
    os.makedirs(SWITCH_DIR, exist_ok=True)
    for key in keys:
        with open(TITLEKEY_PATH, "a") as file:
            file.write(f"{key.rights_id}={key.title_key}")
