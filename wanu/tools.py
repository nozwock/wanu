import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from wanu.defines import APP_CACHE_DIR

NPROC = os.cpu_count()

# Written by ChatGeeepeet...fixed by me -_-


def git_checkout(directory: Path, rev: str):
    assert directory.is_dir()
    subprocess.run(["git", "checkout", rev], cwd=directory, check=True)


class BuildTool:
    """
    DEAD CODE
    """

    hactool_rev = "c2c907430e674614223959f0377f5e71f9e44a4a"
    hacpack_rev = "7845e7be8d03a263c33430f9e8c2512f7c280c88"

    @staticmethod
    def hacpack(rev: str = hacpack_rev) -> Path:
        kind = "Hacpack"
        print(f"Building {kind}")
        with tempfile.TemporaryDirectory() as src_dir:
            subprocess.run(
                ["git", "clone", "https://github.com/The-4n/hacPack", src_dir],
                check=True,
            )

            git_checkout(Path(src_dir), rev)

            print("Renaming config file")
            shutil.move(
                os.path.join(src_dir, "config.mk.template"),
                os.path.join(src_dir, "config.mk"),
            )

            print("Running make")
            assert NPROC is not None
            subprocess.run(["make", "-j", str(NPROC // 2)], cwd=src_dir, check=True)

            # Moving bin from temp dir to cache dir
            filename = f"{kind.lower()}"
            os.makedirs(APP_CACHE_DIR, exist_ok=True)
            dest = os.path.join(APP_CACHE_DIR, filename)
            shutil.move(os.path.join(src_dir, filename), dest)

            return Path(dest)

    @staticmethod
    def hactool(rev: str = hactool_rev) -> Path:
        kind = "Hactool"
        print(f"Building {kind}")
        with tempfile.TemporaryDirectory() as src_dir:
            subprocess.run(
                ["git", "clone", "https://github.com/SciresM/hactool", src_dir],
                check=True,
            )

            git_checkout(Path(src_dir), rev)

            print("Renaming config file")
            shutil.move(
                os.path.join(src_dir, "config.mk.template"),
                os.path.join(src_dir, "config.mk"),
            )

            # Removing line 372 as it causes build to fail on Android
            if os.name == "posix" and os.uname().sysname == "Android":
                print("Removing line 372 from 'main.c'")
                with open(os.path.join(src_dir, "main.c"), "r") as file:
                    lines = file.readlines()
                    fixed_main = "".join(lines[:371] + lines[372:])
                with open(os.path.join(src_dir, "main.c"), "w") as file:
                    file.write(fixed_main)

            print("Running make")
            assert NPROC is not None
            subprocess.run(["make", "-j", str(NPROC // 2)], cwd=src_dir, check=True)

            # Moving bin from temp dir to cache dir
            filename = f"{kind.lower()}"
            os.makedirs(APP_CACHE_DIR, exist_ok=True)
            dest = os.path.join(APP_CACHE_DIR, filename)
            shutil.move(os.path.join(src_dir, filename), dest)

            return Path(dest)
