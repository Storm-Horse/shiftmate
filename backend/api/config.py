from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:////data/shiftmate.db"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 43200  # 30 days

    gmail_user: str = ""
    gmail_app_password: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
