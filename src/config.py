from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    init_db: bool = True
    debug: bool = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
