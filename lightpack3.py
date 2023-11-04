import socket, time, imaplib, re, sys


class Lightpack:

    def __init__(self, host: str, port: int, ledMap: list | None = None):
        self.ledMap = ledMap

        try:  # Try to connect to the server API
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((host, port))
            self.__readResult()
        except ConnectionRefusedError:
            print('Lightpack API server is missing')

    def __readResult(self):  # Return last-command API answer  (call in every local method)
        total_data = []
        data = self.connection.recv(8192)
        total_data.append(data.decode())
        return ''.join(total_data)

    def getProfiles(self):
        cmd = 'getprofiles\n'
        self.connection.send(cmd.encode())
        profiles = self.__readResult()
        return profiles.split(':')[1].rstrip(';\n').split(';')

    def getProfile(self):
        cmd = 'getprofile\n'
        self.connection.send(cmd.encode())
        profile = self.__readResult()
        profile = profile.split(':')[1]
        return profile

    def getStatus(self):
        cmd = 'getstatus\n'
        self.connection.send(cmd.encode())
        status = self.__readResult()
        status = status.split(':')[1]
        return status

    def getCountLeds(self):
        cmd = 'getcountleds\n'
        self.connection.send(cmd.encode())
        count = self.__readResult()
        count = count.split(':')[1]
        return count

    def getAPIStatus(self):
        cmd = 'getstatusapi\n'
        self.connection.send(cmd.encode())
        status = self.__readResult()
        status = status.split(':')[1]
        return status

    def getFPS(self) -> int:
        cmd = 'getfps\n'
        self.connection.send(cmd.encode())
        return int(self.__readResult())

    def getColors(self):
        cmd = 'getcolors\n'
        self.connection.send(cmd.encode())
        return self.__readResult()

    def setColor(self, n, r, g, b):  # Set color to the define LED
        if self.ledMap is None:
            raise TypeError('Set ledMap')
        cmd = 'setcolor:{0}-{1},{2},{3}\n'.format(self.ledMap[n - 1], r, g, b)
        self.connection.send(cmd.encode())
        self.__readResult()

    def setOneColorToAll(self, r, g, b):  # Set one color to all LEDs
        if self.ledMap is None:
            raise TypeError('Set ledMap')
        cmd_str = ''
        for i in self.ledMap:
            cmd_str = str(cmd_str) + str(i) + '-{0},{1},{2};'.format(r, g, b)
        cmd = 'setcolor:' + cmd_str + '\n'
        self.connection.send(cmd.encode())
        self.__readResult()

    def setGamma(self, g):
        cmd = 'setgamma:{0}\n'.format(g)
        self.connection.send(cmd.encode())
        self.__readResult()

    def setSmooth(self, s):
        cmd = 'setsmooth:{0}\n'.format(s)
        self.connection.send(cmd.encode())
        self.__readResult()

    def setBrightness(self, s):
        cmd = 'setbrightness:{0}\n'.format(s)
        self.connection.send(cmd.encode())
        self.__readResult()

    def setProfile(self, p):
        # cmd = 'setprofile:{0}\n'.format(p)
        cmd = 'setprofile:%s\n' % p
        self.connection.send(cmd.encode())
        self.__readResult()

    def lock(self):
        cmd = 'lock\n'
        self.connection.send(cmd.encode())
        self.__readResult()

    def unlock(self):
        cmd = 'unlock\n'
        self.connection.send(cmd.encode())
        self.__readResult()

    def turnOn(self):
        cmd = 'setstatus:on\n'
        self.connection.send(cmd.encode())
        self.__readResult()

    def turnOff(self):
        cmd = 'setstatus:off\n'
        self.connection.send(cmd.encode())
        self.__readResult()

    def disconnect(self):
        self.unlock()
        self.connection.close()
