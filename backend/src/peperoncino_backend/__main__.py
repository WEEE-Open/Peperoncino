"""
Generate GCODE with
vpype read -p -ds 20x20cm circle.svg gwrite --profile gcodemm test.gcode
"""
from random import random, randbytes
import time
import struct
from tqdm import tqdm


@app.command()
def start():
    typer.echo("Starting the program...")
    safe_write(struct.pack('B', 0x00))

@app.command()
def pause():
    typer.echo("Pausing the program...")
    safe_write(struct.pack('B', 0x01))

@app.command()
def reset():
    typer.echo("Resetting the program...")
    safe_write(struct.pack('B', 0x03))

@app.command()
def send(file_path: str):
    typer.echo(f"Sending file: {file_path}")
    with open(file_path, 'r') as f:
        data = f.readlines()
        if len(data) <= MAX_FILE_SIZE:
            safe_write(struct.pack('B', 0x02))
        else:
            debug_console.print("FILE TOO BIG: ONLINE MODE ON")
            safe_write(struct.pack('B', 0x04))

        safe_write(struct.pack('I', len(data)))
        # safe_write(normalize_gcode(data))
        itr = data
        if not DEBUG:
            itr = tqdm(list(itr))
        with open("normalized.gcode", "w") as fs:
            for line in itr:
                fs.write(line)
                # i = 0

                safe_write(line)
                # time.sleep(0.1)
            

@app.command()
def exit():
    typer.echo("Exiting the program...")
    raise typer.Exit()

if __name__ == "__main__":
    app()