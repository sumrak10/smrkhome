from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ADALIGHT_SERVER_HOST: str = '192.168.1.3'
    ADALIGHT_SERVER_PORT: str = '3636'
    LED_COUNT: int = 59
    SERIAL_PORT: str = '/dev/ttyUSB0'
    SERIAL_BAUDRATE: int = 115200


settings = Settings()
