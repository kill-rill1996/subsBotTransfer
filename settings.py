from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    bot_token: str
    channel_id: str
    admins: list
    db_url: str
    payment_token: str
    payment_link: str
    support_contact: str

    # prices
    amount_1: int = 100
    amount_3: int = 300
    amount_inf: int = 1000

    # periods
    months_1: int = 1
    months_3: int = 3
    months_inf: int = -1


settings = Settings()

