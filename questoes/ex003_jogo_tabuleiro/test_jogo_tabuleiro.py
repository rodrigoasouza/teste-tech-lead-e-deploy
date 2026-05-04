import inspect
import itertools
import math

import pytest

from . import jogo_tabuleiro


def test_gerador_implementado_corretamente():
    assert inspect.isgeneratorfunction(jogo_tabuleiro._gerar_combinacoes_sem_loop)


def test_gerador_sequencia_valores():
    valores = list(itertools.islice(jogo_tabuleiro._gerar_combinacoes_sem_loop(), 7))
    assert valores == [1, 1, 2, 4, 7, 13, 24]


def test_gerador_independente_entre_chamadas():
    g1 = jogo_tabuleiro._gerar_combinacoes_sem_loop()
    g2 = jogo_tabuleiro._gerar_combinacoes_sem_loop()
    next(g1)
    next(g1)
    assert next(g2) == 1


@pytest.mark.parametrize("casas", [jogo_tabuleiro.TAMANHO_MINIMO - 1, 0, -5])
def test_tamanho_menor_que_tres_levanta_value_error(casas):
    with pytest.raises(ValueError):
        jogo_tabuleiro.analisar_tabuleiro(casas)


def test_value_error_mensagem_limites():
    with pytest.raises(ValueError, match="2"):
        jogo_tabuleiro.analisar_tabuleiro(2)


@pytest.mark.parametrize("valor", [3.5, "4", None, [], {}, True, False])
def test_tipo_nao_int_levanta_type_error(valor):
    with pytest.raises(TypeError):
        jogo_tabuleiro.analisar_tabuleiro(valor)


def test_subclasse_de_int_levanta_type_error():
    class MeuInt(int):
        pass

    with pytest.raises(TypeError):
        jogo_tabuleiro.analisar_tabuleiro(MeuInt(5))


def test_tipos_dos_valores_retornados():
    resultado = jogo_tabuleiro.analisar_tabuleiro(10)
    assert type(resultado["turnos_minimos"]) is int
    assert type(resultado["probabilidade_otima"]) is float
    assert type(resultado["combinacoes_sem_loop"]) is int


def test_tribonacci_coincide_com_gerador():
    gerador_vals = list(
        itertools.islice(jogo_tabuleiro._gerar_combinacoes_sem_loop(), 15)
    )
    for n, esperado in enumerate(gerador_vals):
        assert jogo_tabuleiro._tribonacci(n) == esperado


def test_tribonacci_entrada_grande():
    t = jogo_tabuleiro._tribonacci(999_999)
    # Deve ser positivo e estritamente maior que o anterior (crescimento monotônico)
    assert t > jogo_tabuleiro._tribonacci(999_998)


@pytest.mark.parametrize(
    "distancia, turnos, esperado",
    [
        (2, 1, 1),
        (3, 1, 1),
        (4, 2, 3),
        (5, 2, 2),
        (6, 2, 1),
        (7, 3, 6),
        (10, 4, 10),
        (12, 4, 1),
    ],
)
def test_caminhos_otimos_formula(distancia, turnos, esperado):
    assert jogo_tabuleiro._caminhos_otimos(distancia, turnos) == esperado


def test_caminhos_otimos_estado_invalido_levanta_assertion_error():
    with pytest.raises(AssertionError):
        jogo_tabuleiro._caminhos_otimos(distancia=0, turnos=10)


def test_limites_altos_nao_causam_erro():
    # O enunciado exige "sem máximo definido"
    resultado = jogo_tabuleiro.analisar_tabuleiro(10_000)
    assert set(resultado.keys()) == {
        "turnos_minimos",
        "probabilidade_otima",
        "combinacoes_sem_loop",
    }
    assert type(resultado["turnos_minimos"]) is int
    assert type(resultado["probabilidade_otima"]) is float
    assert type(resultado["combinacoes_sem_loop"]) is int


def _combinacoes_forca_bruta(distancia: int) -> int:
    count = 0
    for length in range(1, distancia + 1):
        for rolls in itertools.product([1, 2, 3], repeat=length):
            if sum(rolls) == distancia:
                count += 1
    return count


def _probabilidade_forca_bruta(distancia: int) -> float:
    turnos = math.ceil(distancia / 3)
    caminhos = sum(
        1
        for rolls in itertools.product([1, 2, 3], repeat=turnos)
        if sum(rolls) == distancia
    )
    return float(caminhos / (3**turnos))


@pytest.mark.parametrize("casas", range(3, 13))
def test_combinacoes_sem_loop_coincide_com_forca_bruta(casas):
    distancia = casas - 1
    res = jogo_tabuleiro.analisar_tabuleiro(casas)
    assert res["combinacoes_sem_loop"] == _combinacoes_forca_bruta(distancia)


@pytest.mark.parametrize("casas", range(3, 13))
def test_probabilidade_coincide_com_forca_bruta(casas):
    distancia = casas - 1
    esperado = _probabilidade_forca_bruta(distancia)
    assert jogo_tabuleiro.analisar_tabuleiro(casas)[
        "probabilidade_otima"
    ] == pytest.approx(esperado)


@pytest.mark.parametrize("casas", range(3, 20))
def test_turnos_minimos_e_ceil_distancia_dividida_por_3(casas):
    assert jogo_tabuleiro.analisar_tabuleiro(casas)["turnos_minimos"] == math.ceil(
        (casas - 1) / 3
    )
