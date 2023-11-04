import logging
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ADALIGHT_SERVER_HOST: str = '192.168.1.3'
    ADALIGHT_SERVER_PORT: int = 3636
    LED_COUNT: int = 59
    SERIAL_PORT: str = '/dev/ttyUSB0'
    SERIAL_BAUDRATE: int = 115200


settings = Settings()

# create logger
logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
