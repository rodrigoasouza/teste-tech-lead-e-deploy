from inspect import isgeneratorfunction
from unittest.mock import patch

import pytest

from .sequencia_numerica import (
    RAZAO,
    VALOR_INICIAL,
    _gerar_sequencia,
    calcular_valor_sequencia,
)


def _esperado_pa(posicao: int) -> int:
    """Oráculo derivado: fórmula fechada da PA."""
    return VALOR_INICIAL + (posicao - 1) * RAZAO


# Valores hardcoded do enunciado — oráculo independente da fórmula da implementação.
VALORES_DO_ENUNCIADO = [
    (1, 11),
    (2, 18),
    (200, 1404),
    (254, 1782),
    (3542158, 24795110),
]

POSICOES_INVALIDAS = [0, -1, -100]

TIPOS_INVALIDOS = [1.5, "2", None, [], {}, True, False]

FLOATS_INTEIROS_INVALIDOS = [1.0, 2.0, 100.0]

POSICOES_PARA_RAZAO = [1, 10, 100, 1000]

POSICOES_PARA_FORMULA_PA = [1, 5, 10, 50, 100, 1000]


@pytest.mark.parametrize("posicao,esperado", VALORES_DO_ENUNCIADO)
def test_valores_do_enunciado(posicao, esperado):
    assert calcular_valor_sequencia(posicao) == esperado


@pytest.mark.parametrize("posicao", POSICOES_INVALIDAS)
def test_posicao_menor_que_um_levanta_value_error(posicao):
    with pytest.raises(ValueError):
        calcular_valor_sequencia(posicao)


@pytest.mark.parametrize("valor", TIPOS_INVALIDOS)
def test_tipo_nao_int_levanta_type_error(valor):
    with pytest.raises(TypeError):
        calcular_valor_sequencia(valor)


@pytest.mark.parametrize("posicao", POSICOES_PARA_RAZAO)
def test_razao_entre_posicoes_consecutivas(posicao):
    atual = calcular_valor_sequencia(posicao)
    proximo = calcular_valor_sequencia(posicao + 1)
    assert proximo - atual == RAZAO


def test_implementacao_usa_gerador():
    assert isgeneratorfunction(_gerar_sequencia), (
        "_gerar_sequencia deveria ser um gerador real"
    )


@pytest.mark.parametrize("posicao", POSICOES_PARA_FORMULA_PA)
def test_segue_formula_da_pa(posicao):
    assert calcular_valor_sequencia(posicao) == _esperado_pa(posicao)


# Floats inteiros (ex: 2.0) devem rejeitar mesmo sendo
# matematicamente equivalentes a int.
@pytest.mark.parametrize("valor", FLOATS_INTEIROS_INVALIDOS)
def test_float_inteiro_levanta_type_error(valor):
    with pytest.raises(TypeError):
        calcular_valor_sequencia(valor)


# Subclasse de int: type() estrito rejeita — documenta o comportamento esperado.
def test_subclasse_de_int_levanta_type_error():
    class MeuInt(int):
        pass

    with pytest.raises(TypeError):
        calcular_valor_sequencia(MeuInt(5))


# Boundary do limite máximo: exatamente no limite deve aceitar; um acima deve rejeitar.
# Usamos patch para substituir _MAX_POSICAO por um valor pequeno e evitar O(n) alto.
def test_limite_maximo_boundary():
    # Caminho do módulo deve ser relativo ao diretório raiz para o patch funcionar
    target = "questoes.ex002_sequencia_numerica.sequencia_numerica._MAX_POSICAO"
    with patch(target, 10):
        assert calcular_valor_sequencia(10) == _esperado_pa(10)  # no limite: aceita
        with pytest.raises(ValueError, match="10"):
            calcular_valor_sequencia(11)  # um acima: rejeita


# Mensagem do TypeError deve identificar o tipo recebido.
def test_type_error_mensagem_contem_tipo_recebido():
    with pytest.raises(TypeError, match="float"):
        calcular_valor_sequencia(1.5)


# Mensagem do ValueError deve mencionar o valor recebido.
def test_value_error_mensagem_contem_valor_recebido():
    with pytest.raises(ValueError, match="-5"):
        calcular_valor_sequencia(-5)


# A função declara -> int; verifica que o tipo retornado é int e não float ou outro.
def test_retorno_e_int():
    assert type(calcular_valor_sequencia(1)) is int
    assert type(calcular_valor_sequencia(10)) is int


# _gerar_sequencia cria gerador independente a cada chamada (sem estado compartilhado).
def test_gerador_independente_entre_chamadas():
    g1 = _gerar_sequencia()
    g2 = _gerar_sequencia()
    next(g1)  # avança g1
    next(g1)
    assert next(g2) == VALOR_INICIAL  # g2 começa do início
