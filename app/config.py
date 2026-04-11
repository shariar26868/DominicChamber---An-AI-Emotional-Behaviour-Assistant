from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    mongodb_url: str
    db_name: str

    class Config:
        env_file = ".env"

settings = Settings()