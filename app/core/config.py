from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore",
        )
    APP_NAME: str = "Books Microservice"
    DEBUG: bool = False
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB: str = "book_library"

settings = Settings()

