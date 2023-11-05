from Adalight import Adalight
from post_process_functions import death_zone, white_limit
from config import settings


if __name__ == '__main__':
    ada = Adalight(
        server_host=settings.ADALIGHT_SERVER_HOST,
        server_port=settings.ADALIGHT_SERVER_PORT,
        led_count=settings.LED_COUNT,
        serial_port=settings.SERIAL_PORT,
        boudrate=settings.SERIAL_BAUDRATE,
        post_process=[death_zone(), white_limit(settings.LED_COUNT, max_avg_brightness=200)]
    )
    try:
        ada.show()
    except KeyboardInterrupt:
        print('Disconnecting...')
    ada.disconnect()
