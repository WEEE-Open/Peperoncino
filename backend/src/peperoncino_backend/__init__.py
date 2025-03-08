import logging
import os

from dotenv import load_dotenv

try:
    from rich.logging import RichHandler

    handler = RichHandler()
    FORMAT = "%(message)s"
except ImportError:
    from logging import StreamHandler

    handler = StreamHandler()
    FORMAT = "[%(levelname)s] %(name)s : %(message)s"


load_dotenv()
debug = os.environ.get("DEBUG", False)
if isinstance(debug, str):
    if debug in ["1", "true", "True", ""]:
        debug = True
    else:
        debug = False

logging.basicConfig(
    level=logging.DEBUG if debug else logging.INFO, format=FORMAT, handlers=[handler]
)

from .cli import main as main_cli
from .server import main as main_server
