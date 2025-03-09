import logging
import os
import sys

from dotenv import load_dotenv
load_dotenv()

try:
    from rich.logging import RichHandler

    handler = RichHandler()
    FORMAT = "%(message)s"
except ImportError:
    from logging import StreamHandler

    handler = StreamHandler()
    FORMAT = "[%(levelname)s] %(name)s : %(message)s"


debug = os.environ.get("DEBUG", False)
if isinstance(debug, str):
    if debug in ["1", "true", "True", ""]:
        debug = True
    else:
        debug = False

logging.basicConfig(
    level=logging.DEBUG if debug else logging.INFO, format=FORMAT, handlers=[handler]
)
def main():
    try:
        match sys.argv[1]:
            case "cli":
                from .cli import main as main_cli
                main_cli()
            case "server":
                from .server import main as main_server
                main_server()
            case _:
                print("Usage: peperoncino_backend [cli|server]")
                sys.exit(1)
    except IndexError:
        print("Usage: peperoncino_backend [cli|server]")
        sys.exit(1)