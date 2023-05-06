import shutil
import logging
from pathlib import Path
from wanu.defines import APP_CACHE_DIR


class Cache:
    """
    DEAD CODE
    """

    def __init__(self, dir: Path = APP_CACHE_DIR):
        self.dir = dir

    def store_path(self, file_path: Path) -> Path:
        self.dir.mkdir(parents=True, exist_ok=True)
        dst = self.dir.joinpath(file_path)
        if file_path != dst:
            shutil.move(file_path, dst)
        return dst

    def get(self, filename: str) -> Path | None:
        for entry in self.dir.iterdir():
            if entry.name == filename:
                return entry
        return None
