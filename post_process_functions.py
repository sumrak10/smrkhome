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


def white_limit(led_count: int) -> Callable[[list[list[int, int, int]]], list[list[int, int, int]]]:
    max_br = led_count * 600

    def post_process(colors: list[list[int, int, int]]) -> list[list[int, int, int]]:
        br = 0
        limit = 0
        for color in colors:
            br += sum(color)
            if br >= max_br:
                limit = round((max_br - br) / 3)
        colors = list(map(lambda channels: list(map(lambda channel: channel - limit, channels)), colors))
        return colors

    def func(colors_list: list[list[int, int, int]]) -> list[list[int, int, int]]:
        return post_process(colors_list)

    return func
