from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum


class TransportMethod(str, Enum):
    STDIO = "stdio"
    SSE = "sse"


class BrowserSettings(BaseSettings):
    browser_type: str = "chromium"
    headless: bool = True
    verbose: bool = False
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_token: SecretStr | None = Field(
        None,
        help="Secret token for authentication. If not set, no authentication will be required.",
    )

    transport: TransportMethod = Field(TransportMethod.STDIO, help="Transport method")
    host: str = "0.0.0.0"
    port: int = 8000

    browser_config: BrowserSettings = Field(default_factory=BrowserSettings)
    max_search_results: int = 8
    cache_ttl_seconds: int = 4 * 60 * 60  # 4 hours in seconds
    cache_max_size: int = 1024


settings = AppSettings()
