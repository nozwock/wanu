import appdirs
from pathlib import Path

APP_CACHE_DIR = appdirs.user_cache_dir("wanu")
SWITCH_DIR = Path.home().joinpath(".switch")
PRODKEYS_PATH = SWITCH_DIR.joinpath("prod.keys")
TITLEKEY_PATH = SWITCH_DIR.joinpath("title.keys")
