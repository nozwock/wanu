import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from wanu.defines import APP_CACHE_DIR

NPROC = os.cpu_count()

# Written by ChatGeeepeet


def git_checkout(directory: str, rev: str):
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
        src_dir = tempfile.TemporaryDirectory()

        try:
            git_clone = subprocess.run(
                ["git", "clone", "https://github.com/The-4n/hacPack", src_dir.name],
                check=True,
            )
            if git_clone.returncode != 0:
                raise subprocess.CalledProcessError(
                    git_clone.returncode, git_clone.args
                )

            git_checkout(src_dir.name, rev)

            print("Renaming config file")
            shutil.move(
                os.path.join(src_dir.name, "config.mk.template"),
                os.path.join(src_dir.name, "config.mk"),
            )

            print("Running make")
            assert NPROC is not None
            make = subprocess.run(
                ["make", "-j", str(NPROC // 2)], cwd=src_dir.name, check=True
            )
            if make.returncode != 0:
                raise subprocess.CalledProcessError(make.returncode, make.args)

            # Moving bin from temp dir to cache dir
            filename = f"{kind.lower()}"
            os.makedirs(APP_CACHE_DIR, exist_ok=True)
            dest = os.path.join(APP_CACHE_DIR, filename)
            shutil.move(os.path.join(src_dir.name, filename), dest)

            return Path(dest)
        finally:
            src_dir.cleanup()

    @staticmethod
    def hactool(rev: str = hactool_rev) -> Path:
        kind = "Hactool"
        print(f"Building {kind}")
        src_dir = tempfile.TemporaryDirectory()

        try:
            git_clone = subprocess.run(
                ["git", "clone", "https://github.com/SciresM/hactool", src_dir.name],
                check=True,
            )
            if git_clone.returncode != 0:
                raise subprocess.CalledProcessError(
                    git_clone.returncode, git_clone.args
                )

            git_checkout(src_dir.name, rev)

            print("Renaming config file")
            shutil.move(
                os.path.join(src_dir.name, "config.mk.template"),
                os.path.join(src_dir.name, "config.mk"),
            )

            # removing line 372 as it causes build to fail on android
            if os.name == "posix" and os.uname().sysname == "Android":
                print("Removing line 372 from `main.c`")
                with open(os.path.join(src_dir.name, "main.c"), "r") as file:
                    lines = file.readlines()
                    fixed_main = "".join(lines[:371] + lines[372:])
                with open(os.path.join(src_dir.name, "main.c"), "w") as file:
                    file.write(fixed_main)

            print("Running make")
            assert NPROC is not None
            make = subprocess.run(
                ["make", "-j", str(NPROC // 2)], cwd=src_dir.name, check=True
            )
            if make.returncode != 0:
                raise subprocess.CalledProcessError(make.returncode, make.args)

            # Moving bin from temp dir to cache dir
            filename = f"{kind.lower()}.bin"
            os.makedirs(APP_CACHE_DIR, exist_ok=True)
            dest = os.path.join(APP_CACHE_DIR, filename)
            shutil.move(os.path.join(src_dir.name, filename), dest)

            return Path(dest)
        finally:
            src_dir.cleanup()
