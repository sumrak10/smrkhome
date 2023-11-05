from typing import Callable


def death_zone(threshold: int = 15) -> Callable[[list[list[int, int, int]]], list[list[int, int, int]]]:
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


def white_limit(led_count: int, max_limit: int) -> Callable[[list[list[int, int, int]]], list[list[int, int, int]]]:
    max_brightness = led_count * max_limit * 3

    def post_process(colors: list[list[int, int, int]]) -> list[list[int, int, int]]:
        all_leds_brightness = sum(map(lambda channels: sum(channels), colors))
        if all_leds_brightness >= max_brightness:
            limit = round((all_leds_brightness - max_brightness) / 3)
            for i, color in enumerate(colors):
                if sum(color) > max_limit * 3:
                    r = color[0] - limit
                    if r < 0:
                        r = 0
                    g = color[1] - limit
                    if g < 0:
                        g = 0
                    b = color[2] - limit
                    if b < 0:
                        b = 0
                    colors[i] = [r, g, b]
        return colors

    def func(colors_list: list[list[int, int, int]]) -> list[list[int, int, int]]:
        return post_process(colors_list)

    return func
