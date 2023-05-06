import appdirs
from pathlib import Path
import importlib.resources as pkg_resources
from .assets.bin import aarch64_linux

APP_CACHE_DIR = appdirs.user_cache_dir("wanu")
SWITCH_DIR = Path.home().joinpath(".switch")
PRODKEYS_PATH = SWITCH_DIR.joinpath("prod.keys")
TITLEKEY_PATH = SWITCH_DIR.joinpath("title.keys")


HACPACK = pkg_resources.path(aarch64_linux, "hacpack")
HACTOOL = pkg_resources.path(aarch64_linux, "hactool")
HAC2L = pkg_resources.path(aarch64_linux, "hac2l")
