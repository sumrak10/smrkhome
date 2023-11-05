from time import perf_counter, sleep
from typing import Callable

from serial import Serial

from lightpack3 import Lightpack
from config import logger


class Adalight:

    def __init__(self,
                 server_host: str,
                 server_port: int,
                 led_count: int,
                 serial_port: str,
                 boudrate: int,
                 post_process: list[Callable[[list[list[int, int, int]]], list[list[int, int, int]]]] | None = None):
        self.led_count = led_count
        self._post_processing_functions_list = post_process or []

        self._serial_port = serial_port
        self._boudrate = boudrate

        logger.info(f"Connecting to serial port {serial_port} with boudrate {boudrate}")
        self._ser = Serial(serial_port)
        logger.info(f"Connected to serial port!")
        self._ser.baudrate = boudrate

        self.lpack = Lightpack(server_host, server_port, led_count, ledMap=None)

        logger.info(f"Wait Adalight handshake")
        assert self._ser.read(4) == b"Ada\n", "This is not adalight device!"
        logger.info(f"It's Adalight device!")

    def refresh_connect(self) -> None:
        self._ser = Serial(self._serial_port)
        self._ser.baudrate = self._boudrate

        self.lpack.refresh_connect()

        assert self._ser.read(4) == b"Ada\n", "This is not adalight device!"

    def disconnect(self) -> None:
        self.lpack.disconnect()
        self._ser.close()

    def show(self):
        start = perf_counter()
        fps = 0
        while True:
            time_ = perf_counter() - start
            mode = self.lpack.get_mode()  # 'ambilight', 'moodlamp'
            fps_limit = int(self.lpack.get_fps(mode)) + 1
            # monitoring
            if time_ > 1:
                print(f'Time remained: {time_}')
                print(f'Current FPS: {fps}')
                print(f'Current FPS limit: {fps_limit}')
                print(f'Current mode: {mode}')
                print()
                start = perf_counter()
                fps = 0

            # tick
            self.update_leds()
            fps += 1

            # fps_limit correct
            if fps > fps_limit:
                sleep(1 / fps_limit)

    def update_leds(self) -> None:
        # get data
        colors_list = self.lpack.get_colors()
        if colors_list is None:
            return None

        # post processing data
        for func in self._post_processing_functions_list:
            colors_list = func(colors_list)

        # make header for request
        hi = (self.led_count << 8) & 0xff
        lo = self.led_count & 0xff
        check = int.to_bytes(hi ^ lo ^ 0x55, 1, "big")
        hi = int.to_bytes(hi, 1, "big")
        lo = int.to_bytes(lo, 1, "big")
        header = b"Ada" + hi + lo + check

        colors_string = b"".join([bytes(px) for px in colors_list])

        # sending request
        self._ser.write(header + colors_string)
