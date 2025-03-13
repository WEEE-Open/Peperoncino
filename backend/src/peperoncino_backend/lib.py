import logging
import struct

import serial
import serial.tools.list_ports

from .consts import MAX_FILE_SIZE

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(_):
        return _


log = logging.getLogger(__name__)


class Plotter:
    def __init__(self, port: str = None):
        self._running = False
        self._uploaded = None
        self._speed = 100
        if port is None:
            ports = get_available_ports()
            ports = list(filter(lambda x: "CP2102" in str(x), ports))
            if ports:
                port = ports[0]["device"]
            else:
                ports = list(
                    filter(
                        lambda x: any(
                            [
                                y is not None
                                for y in [
                                    x["vid"],
                                    x["pid"],
                                    x["hwid"],
                                    x["serial_number"],
                                ]
                            ]
                        ),
                        ports,
                    ),
                )
                if ports:
                    port = ports[0]["device"]
                else:
                    log.warning(
                        "No port provided and none could be automatically selected."
                    )
            if port:
                log.info(f"No port provided. Defaulting to {port}.")
        self.port = port

    @property
    def state(self):
        return self._uploaded, self._running

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if not hasattr(self, "_port") or value != self._port:
            self.serial = self._connect(value)
        self._port = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value: int):
        if value < 0 or value > 200:
            log.error("Speed must be between 0 and 200")
            return

        if value != self._speed:
            self._speed = value
            # Delay is 0 for speed 200, ~10 for speed 100 and 50 for speed 0
            delay = (value - 200) ** 2 / 800
            self.safe_write(struct.pack("B", 0x05))
            self.safe_write(struct.pack("d", delay))

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
        self._running = True
        # TODO: Start a thread to wait for the plotter to send a stop signal

    def pause(self):
        self.safe_write(struct.pack("B", 0x01))
        self._running = False

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

        self._uploaded = file_path
        self.safe_write(struct.pack("I", len(data)))
        itr = tqdm(list(data))
        for line in itr:
            self.safe_write(line)

    def _read_confirmation(self) -> int | None:
        if self.serial:
            line = self.serial.readline()
            if line.startswith("Done"):
                return int(line.strip().split(' ')[-1])

    def check_confirmation(self):
        if self._read_confirmation:
            self._running = False


def get_available_ports() -> list[dict]:
    def jsonserialize(device):
        return {
            "device": device.device,
            "name": device.name,
            "description": device.description,
            "hwid": device.hwid,
            "vid": device.vid,
            "pid": device.pid,
            "serial_number": device.serial_number,
            "location": device.location,
            "manufacturer": device.manufacturer,
            "product": device.product,
            "interface": device.interface,
        }

    ports = sorted(
        serial.tools.list_ports.comports(include_links=False),
        key=lambda x: (x.vid is None, x),
    )
    return [jsonserialize(port) for port in ports]
