import json
import os
import time
from decimal import Decimal
from typing import Any, Dict, Optional, cast

from src.infra.logger import get_logger

logger = get_logger("PersistentCache")


class PersistentCache:
    """
    Um cache simples baseado em arquivo JSON para persistência entre reinicializações.
    Ideal para dados que mudam pouco (como salário mínimo).
    """

    def __init__(self, cache_file: str = ".cache/salario_cache.json"):
        self.cache_file = cache_file
        self._ensure_dir()
        self._data: Dict[str, Any] = self._load()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return cast(Dict[str, Any], json.load(f))
            except Exception as e:
                logger.warning(f"Falha ao carregar cache persistente: {e}")
        return {}

    def _save(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Falha ao salvar cache persistente: {e}")

    def get(self, key: str) -> Optional[Any]:
        item = self._data.get(key)
        if not item:
            return None

        # Verifica expiração (timestamp unix)
        if time.time() > item.get("expires_at", 0):
            return None

        return item.get("value")

    def set(self, key: str, value: Any, ttl_seconds: int):
        self._data[key] = {"value": value, "expires_at": time.time() + ttl_seconds}
        self._save()

    def get_decimal(self, key: str) -> Optional[Decimal]:
        val = self.get(key)
        return Decimal(str(val)) if val is not None else None

    def set_decimal(self, key: str, value: Decimal, ttl_seconds: int):
        self.set(key, float(value), ttl_seconds)
