import os
import platform
from pathlib import Path
from typing import Iterator

from wanu.defines import HACTOOL, PRODKEYS_PATH, TITLEKEY_PATH


def get_files_with_ext(from_dir: Path, ext: str) -> Iterator[Path]:
    assert from_dir.is_dir()
    for path in from_dir.rglob(f"*.{ext}"):
        yield path


def validate_system():
    system = platform.system()
    machine = platform.machine()

    if system != "Linux" or machine != "aarch64":
        raise SystemError(
            "This script is intended to run on Linux with aarch64 architecture only."
        )
