from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from wanu.defines import SWITCH_DIR, TITLEKEY_PATH


@dataclass
class TitleKey:
    rights_id: str
    key: str

    @classmethod
    def new(cls, tik_file: Path) -> TitleKey | None:
        assert tik_file.is_file()
        tik_content = subprocess.run(
            ["xxd", tik_file], capture_output=True, text=True
        ).stdout
        rights_id_match = re.search(r"(?<=2a0: ).{39}", tik_content)
        key_match = re.search(r"(?<=180: ).{39}", tik_content)

        if rights_id_match and key_match:
            rights_id = rights_id_match.group(0).replace(" ", "")
            key = key_match.group(0).replace(" ", "")
            return cls(rights_id, key)
        return None


def store_title_key(keys: Iterable[TitleKey]) -> None:
    os.makedirs(SWITCH_DIR, exist_ok=True)
    for key in keys:
        with open(TITLEKEY_PATH, "a") as file:
            file.write(f"{key.rights_id}={key.key}")
