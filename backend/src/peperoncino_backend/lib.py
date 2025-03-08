import logging
import struct

import serial

from .consts import MAX_FILE_SIZE

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda _: _

log = logging.getLogger(__name__)

class Plotter:
    def __init__(self, port: str):
        self.port = port

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if not hasattr(self, "_port") or value != self._port:
            self.serial = self._connect(value)
        self._port = value

    def _connect(self, serial_port: str):
        if not serial_port:
            log.warning("No port provided. Using debug mode.")
            return None

        try:
            arduino = serial.Serial(
                port=serial_port, baudrate=115200, timeout=0.1, write_timeout=None
            )
            # arduino.set_low_latency_mode(True)
            self.arduino = arduino  # type: ignore
            log.debug(f"Connected to {serial_port}")
        except serial.SerialException:
            log.warning("Port not found. Using debug mode.")
            arduino = None

        return arduino

    def safe_write(self, data):
        if isinstance(data, str):
            data = data.encode("ascii")

        if self.serial:
            log.debug(f"writing {data}")
            self.serial.write(data)
        else:
            log.debug(f"would write {data}")

    def start(self):
        self.safe_write(struct.pack("B", 0x00))

    def pause(self):
        self.safe_write(struct.pack("B", 0x01))

    def reset(self):
        self.safe_write(struct.pack("B", 0x03))

    def send(self, file_path: str):
        log.info(f"Sending file: {file_path}")

        try:
            with open(file_path, "r") as f:
                data = f.readlines()
        except FileNotFoundError:
            log.error(f"File not found: {file_path}")
            return

        if len(data) <= MAX_FILE_SIZE:
            self.safe_write(struct.pack("B", 0x02))
        else:
            log.info("FILE TOO BIG: ONLINE MODE ON")
            self.safe_write(struct.pack("B", 0x04))

        self.safe_write(struct.pack("I", len(data)))
        itr = tqdm(list(data))
        for line in itr:
            self.safe_write(line)
