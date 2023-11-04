from time import perf_counter, sleep

from serial import Serial

from lightpack3 import Lightpack, Commands


class Adalight:

    def __init__(self, server_host: str, server_port: int, led_count: int, serial_port: str, boudrate: int):
        self.led_count = led_count
        self._post_processing_functions_list = []

        self._serial_port = serial_port
        self._boudrate = boudrate

        self._ser = Serial(serial_port)
        print(f"Connected to serial port {serial_port}")
        self._ser.baudrate = boudrate

        self.lpack = Lightpack(server_host, server_port, ledMap=None)
        print(f"Connected to Adalight server {server_host}:{server_port}")
        assert self._ser.read(4) == b"Ada\n", "This is not adalight device!"

        self.__remaining = ''

    def refresh_connect(self) -> None:
        self._ser = Serial(self._serial_port)
        self._ser.baudrate = self._boudrate

        self.lpack.refresh_connect()

        assert self._ser.read(4) == b"Ada\n", "This is not adalight device!"

        self.__remaining = ''

    def disconnect(self) -> None:
        self.__remaining = ''
        self.lpack.disconnect()
        self._ser.close()

    def show(self):
        start = perf_counter()
        frames_counter = 0
        while True:
            time_ = perf_counter() - start

            fps = self.lpack.execute(Commands.GET_FPS) + 1
            mode = self.lpack.execute(Commands.GET_MODE)  # 'ambilight', 'moodlamp'
            print(time_)
            # monitoring
            if time_ > 1:
                print(f'Time remained: {time_}')
                print(f'Frames in sec: {frames_counter}')
                print(f'Current server FPS: {fps}')
                print(f'Current mode: {mode}')
                start = perf_counter()
                frames_counter = 0

            # tick
            self.update_leds()
            frames_counter += 1

            # FPS correct
            if mode == 'ambilight':
                sleep(1 / fps)
            elif mode == 'moodlamp':
                sleep(1 / 60)

    def update_leds(self) -> None:
        # get and parse data
        colors_string = self.lpack.execute(Commands.GET_COLORS, save_rn = True, save_output = True)
        colors_list, self.__remaining = self.parse_colors_string(colors_string, self.__remaining)
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

    @staticmethod
    def parse_colors_string(string_: str, remaining: str) -> tuple[list[list[int, int, int]], str]:
        string_ = remaining + string_[7:]  # remove prefix
        remaining = string_.split('\r\n')[1]  # slice remaining
        string_ = string_.split('\r\n')[0]  # slice main part
        try:
            list_ = list(filter(lambda x: len(x) > 0, string_.split(';')))  # remove empty elements
            list_ = list(map(lambda x: x.split('-')[1].split(','), list_))  # split string to r,g,b list
            list_ = list(map(lambda x: list(map(lambda y: int(y), x)), list_))  # parse to int
        except IndexError as exc:
            return None
        else:
            return list_, remaining

