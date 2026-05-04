import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Garante a carga do .env no início de tudo
load_dotenv()


class Settings(BaseSettings):
    """
    Configuração Centralizada da Aplicação.
    Utiliza Pydantic Settings para validação de tipos e carregamento automático de .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    # --- Servidor & Infra ---
    app_port: int = Field(default=8080, alias="APP_PORT")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: str = Field(default="WARNING", alias="LOG_LEVEL")
    app_allowed_origins: str = Field(default="", alias="APP_ALLOWED_ORIGINS")
    trust_x_forwarded_for: bool = Field(default=False, alias="TRUST_X_FORWARDED_FOR")
    is_ci: bool = Field(default=False, alias="GITHUB_ACTIONS")

    # --- Performance & Segurança ---
    gzip_min_size: int = Field(default=512, alias="GZIP_MIN_SIZE")
    rate_limit_max: int = Field(default=200, alias="RATE_LIMIT_MAX")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")
    disable_rate_limit: bool = Field(default=False, alias="DISABLE_RATE_LIMIT")

    # --- Services ---
    api_salario_url: str = Field(
        default="https://api.bcb.gov.br/dados/serie/bcdata.sgs.1619/dados/ultimos/1?formato=json",
        alias="API_SALARIO_URL",
    )

    def get_state_salary(self, state_code: str) -> Optional[float]:
        """
        Recupera o salário mínimo configurado para um estado específico.
        Ex: SALARIO_MINIMO_SP
        """
        env_key = f"SALARIO_MINIMO_{state_code.upper()}"
        # Buscamos diretamente no ambiente para chaves dinâmicas
        val = os.getenv(env_key)
        try:
            return float(val) if val else None
        except (ValueError, TypeError):
            return None


# Instância singleton para uso em todo o sistema
settings = Settings()
