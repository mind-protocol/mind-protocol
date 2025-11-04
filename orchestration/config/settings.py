# orchestration/config/settings.py
"""
Pydantic settings for orchestration. All config comes from env (or .env).
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # Fallback for pydantic v1

from pydantic import Field, validator, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        extra='ignore',  # Ignore extra env vars not defined here
        env_file='.env',
        env_file_encoding='utf-8'
    )

    REDIS_URL: str = Field("redis://localhost:6379", env="REDIS_URL")
    FALKORDB_HOST: str = Field("localhost", env="FALKORDB_HOST")
    FALKORDB_PORT: int = Field(6379, env="FALKORDB_PORT")
    DEFAULT_TIMEOUT_SEC: float = Field(30.0, env="DEFAULT_TIMEOUT_SEC")

    # Compose URL in a validator so env overrides work correctly
    FALKORDB_URL: str | None = None

    @validator("FALKORDB_URL", pre=True, always=True)
    def _compose_falkordb_url(cls, v, values):
        if v:
            return v
        host = values.get("FALKORDB_HOST", "localhost")
        port = values.get("FALKORDB_PORT", 6379)
        return f"redis://{host}:{port}"


settings = Settings()  # module-level singleton
