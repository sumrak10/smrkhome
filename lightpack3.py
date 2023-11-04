from typing import Literal
from enum import Enum
from dataclasses import dataclass
import socket


@dataclass
class Command:
    inp_text: str
    out_text: str


class Commands(Enum):
    GET_COLORS = Command('getcolors', 'colors')
    GET_FPS = Command('getfps', 'fps')
    GET_MODE = Command('getmode', 'mode')


class Lightpack:

    def __init__(self, host: str, port: int, ledMap: list | None = None):
        self._ledMap = ledMap
        self._host = host
        self._port = port

        try:  # Try to connect to the server API
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((host, port))
            self.__readResult()
        except ConnectionRefusedError:
            print('Lightpack API server is missing')

    def refresh_connect(self):
        try:  # Try to connect to the server API
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self._host, self._port))
            self.__readResult()
        except ConnectionRefusedError:
            return None

    def disconnect(self):
        # self.unlock()
        self.connection.close()

    def __readResult(self):  # Return last-command API answer  (call in every local method)
        total_data = []
        data = self.connection.recv(8192)
        total_data.append(data.decode())
        return ''.join(total_data)

    def execute(self, command: Commands, save_rn: bool = False, save_output: bool = False):
        self.connection.send(command.value.inp_text.encode())
        res = self.__readResult()
        if not save_rn:
            res = res.replace('\r\n', '')
        if not save_output:
            res = res.replace(command.value.out_text, '')
        return res
    #
    # def getFPS(self) -> int:
    #     cmd = 'getfps\n'
    #     self.connection.send(cmd.encode())
    #     res = self.__readResult().replace('\r\n', '').replace('fps:', '')
    #     return int(res)
    #
    # def get_mode(self) -> Literal['ambilight', 'moodlamp']:
    #     cmd = 'getmode\n'
    #     self.connection.send(cmd.encode())
    #     res = self.__readResult().replace('\r\n', '').replace('mode:', '')
    #     return res
    #
    # def getColors(self):
    #     cmd = 'getcolors\n'
    #     self.connection.send(cmd.encode())
    #     return self.__readResult()
    #
    # def setColor(self, n, r, g, b):  # Set color to the define LED
    #     if self.ledMap is None:
    #         raise TypeError('Set ledMap')
    #     cmd = 'setcolor:{0}-{1},{2},{3}\n'.format(self.ledMap[n - 1], r, g, b)
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def setOneColorToAll(self, r, g, b):  # Set one color to all LEDs
    #     if self.ledMap is None:
    #         raise TypeError('Set ledMap')
    #     cmd_str = ''
    #     for i in self.ledMap:
    #         cmd_str = str(cmd_str) + str(i) + '-{0},{1},{2};'.format(r, g, b)
    #     cmd = 'setcolor:' + cmd_str + '\n'
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def setGamma(self, g):
    #     cmd = 'setgamma:{0}\n'.format(g)
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def setSmooth(self, s):
    #     cmd = 'setsmooth:{0}\n'.format(s)
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def setBrightness(self, s):
    #     cmd = 'setbrightness:{0}\n'.format(s)
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def setProfile(self, p):
    #     # cmd = 'setprofile:{0}\n'.format(p)
    #     cmd = 'setprofile:%s\n' % p
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def lock(self):
    #     cmd = 'lock\n'
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def unlock(self):
    #     cmd = 'unlock\n'
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def turnOn(self):
    #     cmd = 'setstatus:on\n'
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
    #
    # def turnOff(self):
    #     cmd = 'setstatus:off\n'
    #     self.connection.send(cmd.encode())
    #     self.__readResult()
