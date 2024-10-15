from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    bot_token: str
    channel_id: str
    admins: list
    db_url: str
    payment_token: str
    payment_link: str


settings = Settings()

