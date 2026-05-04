import math

import pytest

from .validacao_string import verificar_com_indexacao, verificar_com_metodos_string


class _SubStr(str):
    """str subclass para verificar que isinstance-based dispatch funciona."""


# ---------------------------------------------------------------------------
# Strings válidas (devem retornar True)
# ---------------------------------------------------------------------------
CASOS_VALIDOS = ["BA", "BOLA", "BANANA", "B A", "B!@#$A", "B123A"]

CASOS_ESPECIAIS = [
    "B!A",  # caractere de pontuação no meio
    "B\tA",  # tab
    "B\nA",  # newline
    "B\rA",  # carriage return
]

CASOS_UNICODE_VALIDOS = [
    "BüA",  # acento dentro da string
    "B\U0001f600A",  # emoji fora do BMP
    "B\x00A",  # null byte no meio
]

CASOS_LONGOS = ["B" + "X" * 1000 + "A", "B" + " " * 10000 + "A"]

# ---------------------------------------------------------------------------
# Strings inválidas (devem retornar False)
# ---------------------------------------------------------------------------
CASOS_INVALIDOS_CASE = ["ba", "bA", "Ba"]  # todos/só-início/só-fim minúsculos

CASOS_INVALIDOS_POSICAO = ["AB", "BARCO", "BB", "AA"]

CASOS_INVALIDOS_CONTEUDO = ["B", "A", " "]

CASOS_INVALIDOS_ESPACOS = [" BA", "BA ", " B A "]

# Caracteres visualmente idênticos a B/A mas com codepoints distintos
CASOS_HOMOGLIFOS_INVALIDOS = [
    "ΒA",  # Β (Beta grego U+0392) + A
    "BА",  # B + А (cirílico U+0410)
    "ＢＡ",  # Ｂ + Ａ (fullwidth U+FF22/FF21)
]

# ---------------------------------------------------------------------------
# None e "" — retornam False silenciosamente
# ---------------------------------------------------------------------------
CASOS_NULO_OU_VAZIO = [None, ""]

# ---------------------------------------------------------------------------
# Tipos não-string — levantam TypeError (truthy E falsy, pós-correção do guard)
# ---------------------------------------------------------------------------
CASOS_INVALIDOS_TIPOS = [
    123,
    0,  # int truthy e falsy
    True,
    False,  # bool truthy e falsy (subclasse de int, não de str)
    45.6,
    float("nan"),  # float e float especial
    ["B", "A"],
    [],  # list truthy e falsy
    {},  # dict falsy (mapeamentos também levantam TypeError)
    b"BA",  # bytes — erro comum de quem confunde str com bytes
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _id_caso(valor):
    if isinstance(valor, bytes):
        return f"bytes={valor!r}"
    if isinstance(valor, str):
        return repr(valor) if len(valor) <= 20 else f"str(len={len(valor)})"
    if isinstance(valor, float) and (math.isnan(valor) or math.isinf(valor)):
        return f"float={valor}"
    return f"{type(valor).__name__}={valor!r}"


# ---------------------------------------------------------------------------
# Fixture: roda cada teste contra as duas implementações
# ---------------------------------------------------------------------------
@pytest.fixture(
    params=[verificar_com_metodos_string, verificar_com_indexacao],
    ids=["metodos_string", "indexacao"],
)
def funcao(request):
    return request.param


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------
def test_retorna_bool(funcao):
    assert isinstance(funcao("BA"), bool)
    assert isinstance(funcao("AB"), bool)


@pytest.mark.parametrize("entrada", CASOS_VALIDOS, ids=_id_caso)
def test_strings_validas(funcao, entrada):
    assert funcao(entrada) is True


@pytest.mark.parametrize("entrada", CASOS_ESPECIAIS, ids=_id_caso)
def test_caracteres_especiais(funcao, entrada):
    assert funcao(entrada) is True


@pytest.mark.parametrize("entrada", CASOS_UNICODE_VALIDOS, ids=_id_caso)
def test_unicode_valido(funcao, entrada):
    assert funcao(entrada) is True


@pytest.mark.parametrize("entrada", CASOS_LONGOS, ids=lambda v: f"len={len(v)}")
def test_string_muito_longa(funcao, entrada):
    assert funcao(entrada) is True


@pytest.mark.parametrize("entrada", CASOS_INVALIDOS_CASE, ids=_id_caso)
def test_case_sensitivity(funcao, entrada):
    assert funcao(entrada) is False


@pytest.mark.parametrize("entrada", CASOS_INVALIDOS_POSICAO, ids=_id_caso)
def test_posicao_incorreta(funcao, entrada):
    assert funcao(entrada) is False


@pytest.mark.parametrize("entrada", CASOS_INVALIDOS_CONTEUDO, ids=_id_caso)
def test_conteudo_invalido(funcao, entrada):
    assert funcao(entrada) is False


@pytest.mark.parametrize("entrada", CASOS_INVALIDOS_ESPACOS, ids=_id_caso)
def test_espacos_nas_extremidades(funcao, entrada):
    assert funcao(entrada) is False


@pytest.mark.parametrize("entrada", CASOS_HOMOGLIFOS_INVALIDOS, ids=_id_caso)
def test_homoglifos_retornam_false(funcao, entrada):
    """Codepoints distintos de B/A não devem ser aceitos mesmo parecendo iguais."""
    assert funcao(entrada) is False


@pytest.mark.parametrize("entrada", CASOS_NULO_OU_VAZIO, ids=_id_caso)
def test_nulo_e_vazio_retornam_false(funcao, entrada):
    assert funcao(entrada) is False


@pytest.mark.parametrize("entrada", CASOS_INVALIDOS_TIPOS, ids=_id_caso)
def test_tipos_invalidos_levantam_type_error(funcao, entrada):
    with pytest.raises(TypeError, match="Esperado str"):
        funcao(entrada)


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        (_SubStr("BA"), True),
        (_SubStr("AB"), False),
        (_SubStr(""), False),
    ],
)
def test_subclasse_de_str(funcao, entrada, esperado):
    # Garante que é realmente subclasse (type is not str, mas isinstance é True)
    assert type(entrada) is _SubStr
    assert isinstance(entrada, str)
    # A função usa isinstance(), portanto subclasses devem ser aceitas normalmente
    assert funcao(entrada) is esperado


def test_string_um_caractere(funcao):
    """Strings de 1 caractere nunca satisfazem as duas condições simultaneamente."""
    assert funcao("B") is False  # começa com B mas não termina com A
    assert funcao("A") is False  # termina com A mas não começa com B
    assert funcao("X") is False  # nem uma coisa nem outra


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("BXXX", False),  # começa com B, mas não termina com A
        ("XXXA", False),  # termina com A, mas não começa com B
        ("XXXX", False),  # nenhuma das condições
        ("BA", True),  # ambas as condições — mínimo válido
    ],
    ids=_id_caso,
)
def test_ambas_condicoes_necessarias(funcao, entrada, esperado):
    """Valida que as condições são AND: ambas precisam ser verdadeiras."""
    assert funcao(entrada) is esperado
