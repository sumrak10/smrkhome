import asyncio
from time import perf_counter, sleep

from serial import Serial

import numpy as np

import lightpack3


def parse_colors_string(string_: str) -> tuple[str, list[tuple[int, int, int]]]:
    try:
        string_ = string_[7:]  # remove prefix
        string_ = string_.replace('\r\n', '')
        list_ = list(filter(lambda x: len(x) > 0, string_.split(';')))  # remove empty elements
        list_ = list(map(lambda x: x.split('-')[1].split(','), list_))  # split string to r,g,b list
        list_ = list(map(lambda x: list(map(lambda y: int(y), x)), list_))  # make from list -> tuple and parse to int
    except Exception as exc:
        print(exc)
        print(string_)
        return None
    else:
        return list_


class Adalight:

    def __init__(self, led_count: int, port: str):
        self._port = port
        self._ser = None
        self.led_count = led_count

    def connect(self) -> None:
        if isinstance(self._ser, Serial) and self._ser.is_open:
            self._ser.close()

        assert self._port is not None, "Port is not set!"

        self._ser = Serial(self._port, 115200)
        assert self._ser.read(4) == b"Ada\n", "This is not adalight device!"

    def disconnect(self) -> None:
        if isinstance(self._ser, Serial) and self._ser.is_open:
            self._ser.close()
        self._ser = None

    def writeZones(self, zones: list) -> None:
        if not isinstance(self._ser, Serial) or not self._ser.is_open: return
        self._ser.write(self.mkHeader() + self.mkPayload(zones))

    def mkHeader(self) -> bytes:
        hi = (self.led_count << 8) & 0xff
        lo = self.led_count & 0xff

        check = int.to_bytes(hi ^ lo ^ 0x55, 1, "big")
        hi = int.to_bytes(hi, 1, "big")
        lo = int.to_bytes(lo, 1, "big")
        return b"Ada" + hi + lo + check

    def mkPayload(self, zones: list) -> bytes:
        return b"".join([bytes(px) for px in zones])


async def main():
    lpack = lightpack3.Lightpack('127.0.0.1', 3636, )
    ada = Adalight(led_count=59, port='COM9')
    ada.connect()
    # try:
    i = 0
    start = perf_counter()
    while True:
        if i % 60 == 0:
            i = 0
            print(perf_counter() - start)
            start = perf_counter()
            fps = lpack.getFPS()
            print(fps)
        s = lpack.getColors()
        s = parse_colors_string(s)
        if s is None:
            continue
        ada.writeZones(s)
    # except Exception as exc:
    #     print(exc)
    ada.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
