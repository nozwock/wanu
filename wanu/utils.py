import os
from pathlib import Path
from typing import Iterable
from enum import Enum
import subprocess
import re
from wanu.defines import HACTOOL


def get_files_with_ext(from_dir: Path, ext: str) -> Iterable[Path]:
    for file in os.listdir(from_dir):
        if file.endswith(ext):
            yield Path(file)


class ContentType(Enum):
    Program = (0x00,)
    Meta = (0x01,)
    Control = (0x02,)
    Manual = (0x03,)
    Data = (0x04,)
    PublicData = (0x05,)


def get_content_type(rom: Path) -> str:
    output = subprocess.check_output([HACTOOL, rom], universal_newlines=True)
    content_type = re.search(r"Content Type:\s{23}(.*)", output)
    if content_type:
        return content_type.group(1).strip()
    raise Exception("Failed to process ContentType")