import itertools
from typing import Final, cast

VALOR_INICIAL: Final[int] = 11
RAZAO: Final[int] = 7
# Limite prático: ~100M evita bloqueio indefinido do processo
_MAX_POSICAO: Final[int] = 100_000_000


def _gerar_sequencia():
    valor = VALOR_INICIAL
    while True:
        yield valor
        valor += RAZAO


def calcular_valor_sequencia(posicao: int) -> int:
    """Retorna o valor da sequência aritmética na posição dada (1-indexed)."""
    if type(posicao) is not int:
        raise TypeError(
            f"A posição deve ser um número inteiro, mas foi recebido "
            f"{type(posicao).__name__!r}."
        )
    if posicao < 1:
        raise ValueError(f"A posição deve ser >= 1, mas foi recebido {posicao}.")
    if posicao > _MAX_POSICAO:
        raise ValueError(
            f"A posição deve ser <= {_MAX_POSICAO}, mas foi recebido {posicao}."
        )

    it = _gerar_sequencia()
    resultado = next(itertools.islice(it, posicao - 1, None), None)

    if resultado is None:
        raise RuntimeError(f"Gerador esgotado inesperadamente na posição {posicao}.")

    return cast(int, resultado)
