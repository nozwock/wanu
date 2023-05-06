import importlib.resources as pkg_resources
from pathlib import Path

import appdirs

from .assets.bin import aarch64_linux

APP_CACHE_DIR = appdirs.user_cache_dir("wanu")
SWITCH_DIR = Path.home().joinpath(".switch")
PRODKEYS_PATH = SWITCH_DIR.joinpath("prod.keys")
TITLEKEY_PATH = SWITCH_DIR.joinpath("title.keys")


HACPACK = Path(str(pkg_resources.path(aarch64_linux, "hacpack")))
HACTOOL = Path(str(pkg_resources.path(aarch64_linux, "hactool")))
HAC2L = Path(str(pkg_resources.path(aarch64_linux, "hac2l")))
