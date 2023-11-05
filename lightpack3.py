from time import sleep
import socket
from typing import Literal

from config import logger


class Lightpack:

    def __init__(self, host: str, port: int, led_count: int, ledMap: list | None = None):
        self._ledMap = ledMap
        self._host = host
        self._port = port

        self.led_count = led_count
        self.is_locked = False
        self.colors_remaining = ''

        logger.info(f"Connecting to Adalight server {host}:{port}")
        for i in range(5):
            try:  # Try to connect to the server API
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.connect((host, port))
                self.__readResult()
                break
            except ConnectionRefusedError:
                logger.warning(f"Connection refused {i}")
                sleep(1)
        else:
            raise ConnectionRefusedError()
        logger.info(f"Connected to Adalight server!")

    def refresh_connect(self) -> bool:
        try:
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.connect((self._host, self._port))
            self.__readResult()
            return True
        except:
            return False

    def disconnect(self):
        # self.unlock()
        self.connection.close()

    def __readResult(self):  # Return last-command API answer  (call in every local method)
        total_data = []
        data = self.connection.recv(8192)
        total_data.append(data.decode())
        return ''.join(total_data)

    def exit(self):
        """
        Команда закрывает подключение к серверу и доступна постоянно.
        """
        self.connection.send('exit\n'.encode())
        self.disconnect()

    def api_key(self, key: str) -> bool:
        """
        Отправляет серверу строку ключа авторизации. Если строка совпадает с заданной в программе,
        сервер авторизует подключение и у пользователя появляется доступ ко всем командам API.
        """
        cmd = f'apikey:{key}\n'
        self.connection.send(cmd.encode())
        res = self.__readResult().replace('\r\n', '')
        if res == 'ok':
            return True
        return False

    def _get(self, command_text: str, original: bool = False) -> str:
        cmd = command_text + '\n'
        self.connection.send(cmd.encode())
        res = self.__readResult()
        if not original:
            res = res.replace('\r\n', '')
            res = res.replace(command_text.replace('get', '') + ':', '')
        return res

    def _set(self, command_text: str, setting_value: str | None = None, original: bool = False,
             lock_if_not: bool = True) -> str:
        if not self.is_locked and lock_if_not:
            self.lock()
        if setting_value is not None:
            cmd = command_text + ':' + setting_value + '\n'
        else:
            cmd = command_text + '\n'
        self.connection.send(cmd.encode())
        res = self.__readResult()
        if not original:
            res = res.replace('\r\n', '')
            res = res.replace(command_text + ':', '')
        return res

    def get_status(self) -> Literal['on', 'off', 'device error', 'unknown']:
        """
        Возвращаемые значения: on, off, device error или unknown.
        Возвращает состояние устройства, которое, будучи подключенным к ПК может быть
        выключено (светодиоды не горят), или включено в настройках программы захвата.
        Команда возвращает device error в случае ошибки доступа к устройству (иконка в
        трее меняется на запрещающую). Unknown -- маловероятное событие, которое происходит
        при истечении таймаута запроса к GUI (~1 с.)
        """
        return self._get('getstatus')

    def get_status_api(self) -> Literal['idle', 'busy']:
        """
        Возвращаемые значения: idle или busy.
        Возвращает текущее состояние API устройства. API занят в том случае, если
        управление устройством осуществляется извне (вами, вашим скриптом, кем-то
        по сети и пр.) и свободен если устройством управляет программа захвата.
        До тех пор, пока не будет выполнена команда lock (см. ниже) API не может быть занят.
        """
        return self._get('getstatusapi')

    def get_profiles(self) -> list[str]:
        """
        Возвращает полный список профилей настроек управляющей программы через ';'. Профили хранятся в папке Profiles.
        """
        res = self._get('getprofiles')
        return res.split(';')

    def get_profile(self) -> str:
        """
        Возвращает имя текущего активного профиля.
        """
        return self._get('getprofile')

    def get_count_leds(self) -> int:
        """
        Начиная с версии 5.8 управляющей программы у пользователя появилась возможность управлять
        с её помощью разными устройствами. Для некоторых из них пользователь может
        самостоятельно выбирать количество зон захвата от 1 до 50 по количеству используемых светодиодов.
        Команда возвращает общее количество всех зон захвата (активных и отключенных) в текущем профиле.
        """
        return int(self._get('getcountleds'))

    def get_mode(self) -> Literal['ambilight', 'moodlamp', 'soundviz']:
        """
        Возвращаемые значения: ambilight, moodlamp, soundviz, и подобное (плагины)
        Команда возвращает текущий режим работы подсветки.
        """
        return self._get('getmode')

    def get_fps(self, mode: str | None = None) -> int:
        """
        Возвращает значение счётчика FPS (Frames Per Second) для режима ambilight.
        """
        if mode is None:
            mode = self.get_mode()
        if mode == 'ambilight':
            return int(self._get('getfps'))
        else:
            return 40

    def get_leds(self) -> list[list[int, int, int, int]]:
        """
        Возвращает настройки зон захвата в формате N - X, Y, W, H; Где N -- номер области захвата.
        X, Y -- координаты левого верхнего угла области.
        W, H -- ширина и высота области в пикселях.
        """
        res = self._get('getleds', True)
        # TODO
        return [[1, 1, 1, 1], [2, 2, 2, 2]]

    def get_colors(self) -> list[list[int, int, int]] | None:
        """
        Возвращает цвет, выводимый на светодиоды в настоящий момент времени в формате R, G, B.
        Где R, G, B -- соответствующие цветовые компоненты.
        """
        # 1  ---  colors:1,2,3;1,2,3;\r\n\                ->      main: + remaining: -
        # 2  ---  colors:1,2,3;1,2,3;\r\n\colors:1,2,     ->      main: + remaining: +
        # 3  ---  3;1,2,3;\r\n\colors:1,2                 ->      main: + remaining: -
        # 4  ---  ,3;1,2,3;                               ->      main: + remaining: -
        all_string = self.colors_remaining + self._get('getcolors', True)
        main_string = ''
        remaining_string = ''

        if all_string.startswith('colors:') and all_string.endswith('\r\n'):
            main_string = all_string.replace('colors:', '').replace('\r\n', '')
        elif all_string.startswith('colors:'):
            main_string = all_string.split('\r\n', 1)[0]
            main_string = main_string.replace('colors:', '')
            remaining_string = all_string.split('\r\n', 1)[1]

        self.colors_remaining = remaining_string
        if main_string != '':
            list_ = list(filter(lambda x: len(x) > 0, main_string.split(';')))  # remove empty elements
            list_ = list(map(lambda x: x.split('-')[1].split(','), list_))  # split string to r,g,b list
            list_ = list(map(lambda x: list(map(lambda y: int(y), x)), list_))  # parse to int
            if len(list_) != self.led_count:
                return list_
        self.colors_remaining = all_string
        return None

    def lock(self) -> Literal['success', 'busy', 'locked_now']:
        if not self.is_locked:
            res = self._set('lock', lock_if_not=False)
            if res == 'success':
                self.is_locked = True
        else:
            res = 'locked_now'
        return res

    def unlock(self) -> tuple[bool, Literal['success', 'not_locked']]:
        if self.is_locked:
            res = self._set('unlock', lock_if_not=False)
            if res == 'success':
                self.is_locked = False
            return res
        else:
            res = 'not_locked'
        return res

    def set_color(self, n: int, r: int, g: int, b: int) -> bool:
        cmd = f'{n}-{r},{g},{b};'
        res = self._set('setcolor', cmd)
        if res == 'ok':
            return True
        return False

    def set_colors(self, colors: list[list[int, int, int]]) -> bool:
        cmd = ''
        for n, color in enumerate(colors):
            cmd += f'{n}-{color[0]},{color[1]},{color[2]};'
        res = self._set('setcolor', cmd)
        if res == 'ok':
            return True
        return False

    def set_gamma(self, n: float) -> bool:
        cmd = 'setgamma'
        if 0.01 > n > 10.00:
            raise TypeError('Gamma in 0.01 < n < 10.00')
        res = self._set(cmd, str(n))
        if res == 'ok':
            return True
        return False

    def set_smooth(self, n: int) -> bool:
        cmd = 'setsmooth'
        if 0 > n > 255:
            raise TypeError('Smooth in 0 < n < 255')
        res = self._set(cmd, str(n))
        if res == 'ok':
            return True
        return False

    def set_brightness(self, n: int) -> bool:
        cmd = 'setbrightness'
        if 0 > n > 255:
            raise TypeError('Smooth in 0 < n < 255')
        res = self._set(cmd, str(n))
        if res == 'ok':
            return True
        return False

    def set_profile(self, name: str) -> bool:
        cmd = 'setprofile'
        res = self._set(cmd, name)
        if res == 'ok':
            return True
        return False

    def set_status(self, v: bool) -> bool:
        if v:
            cmd = 'on'
        else:
            cmd = 'off'
        res = self._set('setstatus', v)
        if res == 'ok':
            return True
        return False

    def set_mode(self, name: Literal['ambilight', 'moodlamp', 'soundviz']) -> bool:
        cmd = 'setmode'
        res = self._set(cmd, name)
        if res == 'ok':
            return True
        return False
