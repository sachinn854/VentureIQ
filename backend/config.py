from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent / '.env'


class Settings(BaseSettings):
    openrouter_api_key: str
    tavily_api_key: str
    model_name: str = 'anthropic/claude-sonnet-4-6'
    allowed_origin: str = 'http://localhost:5173'
    debug: bool = False

    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding='utf-8')


settings = Settings()
