from random import random, randbytes
import time
import serial
import struct
import typer
from rich.console import Console

MAX_DAC_BITS = 12
BUFFER_SIZE = 4

console = Console()
debug_console = Console(style="bold red")
err_console = Console(stderr=True)

try:
    arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)
except serial.SerialException:
    typer.echo("Port not found. Using debug mode.")
    arduino = None

def safe_write(data):
    if isinstance(data, str):
        data = data.encode('ascii')

    if arduino:
        debug_console.print(f"DEBUG: writing {data}")
        # print(arduino.out_waiting)
        # while arduino.out_waiting >= BUFFER_SIZE:
            # pass
        arduino.write(data)
    else:
        debug_console.print(f"DEBUG: would write {data}")

def normalize_gcode(gcode: list[str]):
    # for each line, find the maximum and min values of x or y
    cur_max = 0
    cur_min = 0xFFFFFFFF
    for line in gcode:
        # lines like G00 X7.3388 Y2.3926\n
        if line.startswith('G0') and line[2] in ['0', '1']:
            x = float(line.split('X')[1].split(' ')[0])
            y = float(line.split('Y')[1].split(' ')[0])
            cur_max = max(cur_max, x, y)
            cur_min = min(cur_min, x, y)
    debug_console.print(f"DEBUG: cur_max: {cur_max}, cur_min: {cur_min}")
    # rescale to MAX_BITS unsigned bits, truncate to int and yield
    for i, line in enumerate(gcode):
        if line.startswith('G0') and line[2] in ['0', '1']:
            old_x = line.split('X')[1].split(' ')[0]
            old_y = line.split('Y')[1].split(' ')[0]
            x = int(((float(old_x) - cur_min) / (cur_max - cur_min)) * (2**MAX_DAC_BITS - 1))
            y = int(((float(old_y) - cur_min) / (cur_max - cur_min)) * (2**MAX_DAC_BITS - 1))
            line = line.replace(old_x, str(x))
            line = line.replace(old_y, str(y))
        if not line.endswith('\n'):
            line += '\n'
        yield line

app = typer.Typer()

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
        safe_write(struct.pack('B', 0x02))
        safe_write(struct.pack('I', len(data)))
        # safe_write(normalize_gcode(data))
        for line in normalize_gcode(data):
            safe_write(line)

@app.command()
def exit():
    typer.echo("Exiting the program...")
    raise typer.Exit()

if __name__ == "__main__":
    app()