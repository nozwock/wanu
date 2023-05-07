import os
import platform
import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Iterator

from wanu.defines import HACTOOL, PRODKEYS_PATH, TITLEKEY_PATH


def get_files_with_ext(from_dir: Path, ext: str) -> Iterator[Path]:
    assert from_dir.is_dir()
    for path in from_dir.rglob(f"*.{ext}"):
        yield path


class ContentType(Enum):
    Program = 0x00
    Meta = 0x01
    Control = 0x02
    Manual = 0x03
    Data = 0x04
    PublicData = 0x05


def get_content_type(rom: Path) -> str | None:
    assert rom.is_file()
    assert PRODKEYS_PATH.is_file()
    output = str(
        subprocess.run(
            [HACTOOL, rom], capture_output=True, universal_newlines=True
        ).stdout
    )
    content_type = re.search(r"Content\s*Type:\s*(\S*)", output)
    if content_type:
        return content_type.group(1).strip()
    return None


def check_aarch64_linux():
    system = platform.system()
    machine = platform.machine()

    if system != "Linux" or machine != "aarch64":
        raise SystemError(
            "This script is intended to run on Linux with aarch64 architecture only."
        )


def clear_titlekeys():
    try:
        os.remove(TITLEKEY_PATH)
    except FileNotFoundError:
        pass
    except Exception as e:
        raise e
