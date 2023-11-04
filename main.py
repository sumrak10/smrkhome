import asyncio
from time import perf_counter, sleep

from Adalight import Adalight
from config import settings


async def main():
    ada = Adalight(
        server_host=settings.ADALIGHT_SERVER_HOST,
        server_port=settings.ADALIGHT_SERVER_PORT,
        led_count=settings.LED_COUNT,
        serial_port=settings.SERIAL_PORT,
        boudrate=settings.SERIAL_BAUDRATE
    )
    try:
        ada.show()
    except Exception as exc:
        print(exc)
    ada.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
