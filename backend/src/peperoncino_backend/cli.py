import os
import sys

import typer
from dotenv import load_dotenv

from .lib import Plotter

load_dotenv()


def main():
    sys.argv = sys.argv[1:]
    app = typer.Typer()

    def execute_command(command: str, port: str, file_path: str = None):
        if port is None:
            port = os.getenv("PLOTTER_SERIAL_PORT")
            if port is None:
                raise typer.BadParameter(
                    "Port must be specified either via --port/-p or PLOTTER_SERIAL_PORT environment variable."
                )
        plotter = Plotter(port)
        if command == "start":
            plotter.start()
        elif command == "pause":
            plotter.pause()
        elif command == "reset":
            plotter.reset()
        elif command == "send":
            if file_path is None:
                raise typer.BadParameter(
                    "The send command requires specifying a path to the gcode file."
                )
            plotter.send(file_path)
        else:
            raise typer.BadParameter(f"Unknown command: {command}")

    port_option = typer.Option(
        os.getenv("PLOTTER_SERIAL_PORT"),
        "--port",
        "-p",
        help="Serial port of the plotter controller",
    )

    @app.command()
    def start(port: str = port_option):
        """Start/Resume the job."""
        execute_command("start", port)

    @app.command()
    def pause(port: str = port_option):
        """Pause the job."""
        execute_command("pause", port)

    @app.command()
    def reset(port: str = port_option):
        """Reset the current job."""
        execute_command("reset", port)

    @app.command()
    def send(
        port: str = port_option,
        file_path: str = typer.Argument(
            ..., help="Path of the gcode file to send to the plotter"
        ),
    ):
        """Send a job to the plotter."""
        execute_command("send", port, file_path)

    app()
