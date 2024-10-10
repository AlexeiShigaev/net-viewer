from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
print("Current app folder: {}".format(BASE_DIR))

STATIC_DIR = BASE_DIR / "static/"


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / "app/.env"
    )


settings = Settings()


def get_auth_data():
    return {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}


