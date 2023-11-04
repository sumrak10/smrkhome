import asyncio
from time import perf_counter, sleep

from Adalight import Adalight
from post_process_functions import death_zone, change_brightness
from config import settings


async def main():
    ada = Adalight(
        server_host=settings.ADALIGHT_SERVER_HOST,
        server_port=settings.ADALIGHT_SERVER_PORT,
        led_count=settings.LED_COUNT,
        serial_port=settings.SERIAL_PORT,
        boudrate=settings.SERIAL_BAUDRATE,
        post_process=[death_zone(), change_brightness()]
    )
    try:
        ada.show()
    except KeyboardInterrupt:
        print('Disconnecting...')
    ada.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
