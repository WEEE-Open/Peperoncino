from enum import Enum
import struct
import serial
import logging

from .consts import MAX_FILE_SIZE

log = logging.getLogger(__name__)

try:
    arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=.1, write_timeout=None)
    # arduino.set_low_latency_mode(True)
except serial.SerialException:
    log.warning("Port not found. Using debug mode.")
    arduino = None

def safe_write(data):
    if isinstance(data, str):
        data = data.encode('ascii')

    if arduino:
        log.debug(f"writing {data}")
        arduino.write(data)
    else:
        log.debug(f"would write {data}")

def start():
    safe_write(struct.pack('B', 0x00))

def pause():
    safe_write(struct.pack('B', 0x01))

def reset():
    safe_write(struct.pack('B', 0x03))

def send(file_path: str):
    log.info(f"Sending file: {file_path}")
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
