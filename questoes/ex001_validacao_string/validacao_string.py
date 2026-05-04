"""Validação de strings que iniciam com 'B' e terminam com 'A'."""

from typing import Final

CARACTERE_INICIAL: Final[str] = "B"
CARACTERE_FINAL: Final[str] = "A"

def verificar_com_metodos_string(texto: object) -> bool:
    """Verifica se texto começa com 'B' e termina com 'A' usando startswith/endswith."""
    if not isinstance(texto, str):
        if texto is None:
            return False
        raise TypeError(f"Esperado str, recebido {type(texto).__name__!r}")

    if not texto:
        return False

    return texto.startswith(CARACTERE_INICIAL) and texto.endswith(CARACTERE_FINAL)
