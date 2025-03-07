import logging
import os

debug = os.environ.get("DEBUG", False)
if isinstance(debug, str):
    if debug in ["1", "true", "True", ""]:
        debug = True
    else:
        debug = False

logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

from .cli import main as main_cli
from .server import main as main_server
