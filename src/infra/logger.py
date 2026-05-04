import logging
import re
import sys

from src.infra.config import settings


class SecretMaskingFilter(logging.Filter):
    """
    Filtro de log que mascara automaticamente padrões de segredos em qualquer mensagem.
    Garante uma camada extra de proteção (DLP) no sistema de logs.
    """

    _PATTERNS = [
        re.compile(
            r"(?i)(password|secret|api_key|token)['\"]?\s*[:=]\s*['\"]([^'\"]{6,})['\"]"
        ),  # Key-Value secrets
        re.compile(r"AIza[0-9A-Za-z-_]{35}"),  # Google API Keys
        re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),  # CPF formatado
        re.compile(r"\b\d{11}\b"),  # CPF desformatado
        re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"),  # CNPJ
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # Email
        re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),  # IPv4
    ]

    def filter(self, record):
        # Render args into msg first
        if record.args:
            try:
                record.msg = record.msg % record.args
            except Exception:  # nosec
                pass
            finally:
                record.args = ()

        if not isinstance(record.msg, str):
            return True

        for pattern in self._PATTERNS:
            record.msg = pattern.sub("***MASKED***", record.msg)

        return True


def configure_logging():
    """
    Configura o sistema de logs dinamicamente.
    """
    app_log_level = settings.log_level.upper()
    app_numeric_level = getattr(logging, app_log_level, logging.WARNING)

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(filename)s:%(lineno)d | %(message)s"
    )

    # Cria o handler e adiciona o filtro de segurança
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.addFilter(SecretMaskingFilter())

    logging.basicConfig(
        level=app_numeric_level,
        format=log_format,
        handlers=[console_handler],
    )

    # Aplica os níveis para as bibliotecas externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("nicegui").setLevel(logging.WARNING)


# Inicializa a configuração global
configure_logging()


def get_logger(name: str):
    """Retorna uma instância do logger devidamente configurada."""
    return logging.getLogger(name)
