import typer
from rich.console import Console
from .lib import start, pause, send, reset

console = Console()
debug_console = Console(style="bold red")
err_console = Console(stderr=True)

app = typer.Typer()
app.command()(start)
app.command()(pause)
def main():
    app()