"""Validação de strings que iniciam com 'B' e terminam com 'A'."""

from typing import Final

CARACTERE_INICIAL: Final[str] = "B"
CARACTERE_FINAL: Final[str] = "A"


def verificar_com_metodos_string(texto: object) -> bool:
    """Verifica se texto começa com 'B' e termina com 'A' usando startswith/endswith."""
    if texto is None or texto == "":
        return False
    if not isinstance(texto, str):
        raise TypeError(f"Esperado str, recebido {type(texto).__name__!r}")
    return texto.startswith(CARACTERE_INICIAL) and texto.endswith(CARACTERE_FINAL)


def verificar_com_indexacao(texto: object) -> bool:
    """Verifica se texto começa com 'B' e termina com 'A' usando indexação."""
    if texto is None or texto == "":
        return False
    if not isinstance(texto, str):
        raise TypeError(f"Esperado str, recebido {type(texto).__name__!r}")
    return texto[0] == CARACTERE_INICIAL and texto[-1] == CARACTERE_FINAL
