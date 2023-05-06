import os
from pathlib import Path
from typing import Iterable


def get_files_with_ext(from_dir: Path, ext: str) -> Iterable[Path]:
    for file in os.listdir(from_dir):
        if file.endswith(ext):
            yield Path(file)
