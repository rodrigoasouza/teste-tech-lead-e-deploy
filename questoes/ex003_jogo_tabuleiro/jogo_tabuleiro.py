from collections.abc import Iterator
from typing import Final

TAMANHO_MINIMO: Final[int] = 3
OPCOES_ROLETA: Final[int] = 3

_TRIBONACCI_MAT: Final = [[1, 1, 1], [1, 0, 0], [0, 1, 0]]


def _mat_mul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    return [
        [A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j] for j in range(3)]
        for i in range(3)
    ]


def _mat_pow(M: list[list[int]], n: int) -> list[list[int]]:
    resultado = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    while n:
        if n & 1:
            resultado = _mat_mul(resultado, M)
        M = _mat_mul(M, M)
        n >>= 1
    return resultado


def _gerar_combinacoes_sem_loop() -> Iterator[int]:
    """Gerador preguiçoso para a sequência (composições de 1, 2 e 3)."""
    a, b, c = 1, 1, 2
    yield a
    yield b
    while True:
        yield c
        a, b, c = b, c, a + b + c


def _tribonacci(n: int) -> int:
    if n <= 1:
        return 1
    M = _mat_pow(_TRIBONACCI_MAT, n - 2)
    return 2 * M[0][0] + M[0][1] + M[0][2]


def _caminhos_otimos(distancia: int, turnos: int) -> int:
    pontos_perdidos = (turnos * OPCOES_ROLETA) - distancia

    if pontos_perdidos == 0:
        return 1
    if pontos_perdidos == 1:
        return turnos
    if pontos_perdidos == 2:
        return turnos * (turnos + 1) // 2

    raise AssertionError(f"Estado inalcançável: pontos_perdidos={pontos_perdidos}")


def analisar_tabuleiro(casas: int) -> dict[str, int | float]:
    """Analisa um tabuleiro unidirecional e retorna as métricas do jogo."""
    if type(casas) is not int:
        raise TypeError(f"Deve ser int, recebido {type(casas).__name__!r}.")
    if casas < TAMANHO_MINIMO:
        raise ValueError(f"Mínimo de {TAMANHO_MINIMO} casas, recebido {casas}.")

    distancia = casas - 1
    turnos_minimos = (distancia + OPCOES_ROLETA - 1) // OPCOES_ROLETA
    total_possibilidades_roleta = OPCOES_ROLETA**turnos_minimos
    caminhos_sucesso = _caminhos_otimos(distancia, turnos_minimos)
    probabilidade = caminhos_sucesso / total_possibilidades_roleta
    combinacoes = _tribonacci(distancia)

    return {
        "turnos_minimos": turnos_minimos,
        "probabilidade_otima": probabilidade,
        "combinacoes_sem_loop": combinacoes,
    }
