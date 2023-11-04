from typing import Callable


def death_zone(threshold: int = 30) -> Callable[[list[list[int, int, int]]], list[list[int, int, int]]]:
    """
    Возвращает полностью черный цвет если все каналы ниже порога threshold
    """

    def post_process(color: list[int, int, int]) -> list[int, int, int]:
        if color[0] < threshold and color[1] < threshold and color[2] < threshold:
            return [0, 0, 0]
        else:
            return [color[0], color[1], color[2]]

    def func(colors_list: list[list[int, int, int]]) -> list[list[int, int, int]]:
        return list(map(post_process, colors_list))

    return func


def change_brightness(value: int = -30) -> Callable[[list[list[int, int, int]]], list[list[int, int, int]]]:
    def post_process(color: list[int, int, int]) -> list[int, int, int]:
        r = color[0] + value
        g = color[1] + value
        b = color[2] + value
        if r < 0:
            r = 0
        if r > 255:
            r = 255
        if g < 0:
            g = 0
        if g > 255:
            g = 255
        if b < 0:
            b = 0
        if b > 255:
            b = 255
        return [r, g, b]

    def func(colors_list: list[list[int, int, int]]) -> list[list[int, int, int]]:
        return list(map(post_process, colors_list))

    return func
