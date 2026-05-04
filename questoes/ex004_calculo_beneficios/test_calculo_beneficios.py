from datetime import date
from decimal import Decimal

import pytest

from .calculo_beneficios import (
    calcular_beneficios_rescisao,
    calcular_decimo_terceiro,
)


def test_decimo_terceiro_integral():
    # Trabalhou o ano todo
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2023, 1, 1),
        data_demissao=date(2023, 12, 31),
    )
    assert res.decimo_terceiro == Decimal("2400.00")
    # Férias proporcionais: também o ano todo (12 meses)
    assert res.ferias_proporcionais == Decimal("2400.00")
    assert res.total == Decimal("4800.00")


def test_decimo_terceiro_meio_ano():
    # Trabalhou até o final de junho (6 meses completos)
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2023, 1, 1),
        data_demissao=date(2023, 6, 30),
    )
    assert res.decimo_terceiro == Decimal("1200.00")  # 6/12
    assert res.ferias_proporcionais == Decimal("1200.00")  # 6/12


def test_dias_trabalhados_limiar():
    # Mês de janeiro: 17 a 31 = 15 dias -> conta 1 mês
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2023, 1, 17),
        data_demissao=date(2023, 12, 31),
    )
    assert res.decimo_terceiro == Decimal("2400.00")

    # Mês de janeiro: 18 a 31 = 14 dias -> não conta o mês de janeiro
    res_menos_um_dia = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2023, 1, 18),
        data_demissao=date(2023, 12, 31),
    )
    assert res_menos_um_dia.decimo_terceiro == Decimal("2200.00")


def test_ferias_aniversario():
    # Admissão em 10/05/2022, demissão em 09/06/2023
    # Aniversário em 10/05/2023. Período: 10/05/2023 a 09/06/2023.
    # 31 dias trabalhados após o aniversário. > 15 dias -> 1 mês.
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2022, 5, 10),
        data_demissao=date(2023, 6, 9),
    )
    assert res.ferias_proporcionais == Decimal("200.00")
    # Décimo terceiro de 2023: trabalhou de jan até 09 de junho.
    # Jan, Fev, Mar, Abr, Mai completos (5 meses).
    # Jun: 1 a 9 = 9 dias. < 15 dias, não conta.
    # Total = 5 meses. 2400 * 5/12 = 1000.
    assert res.decimo_terceiro == Decimal("1000.00")


def test_ano_bissexto():
    # Admissão em 29/02/2020. Demissão em 15/03/2023.
    # Último aniversário de emprego antes de 15/03/2023 foi em 2023.
    # Como 2023 não é bissexto, cai em 28/02/2023.
    # Período: 28/02/2023 a 15/03/2023 = 16 dias. >= 15 dias -> 1 mês.
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2020, 2, 29),
        data_demissao=date(2023, 3, 15),
    )
    assert res.ferias_proporcionais == Decimal("200.00")  # 1/12
    # Décimo terceiro de 2023: Jan e Fev completos. Mar: 15 dias. -> 3 meses
    assert res.decimo_terceiro == Decimal("600.00")  # 3/12


def test_data_invalida():
    with pytest.raises(ValueError, match="não pode ser anterior"):
        calcular_beneficios_rescisao(
            salario=Decimal("2400"),
            data_admissao=date(2023, 12, 31),
            data_demissao=date(2023, 1, 1),
        )


def test_limite_ferias_12_meses():
    # Testar o teto de 12/12 avos nas férias (ex: admitido 01/01 e demitido 20/12)
    # 11 meses completos + 20 dias (que conta como +1 mês) = 12 meses
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2023, 1, 1),
        data_demissao=date(2023, 12, 20),
    )
    assert res.ferias_proporcionais == Decimal("2400.00")
    # Décimo terceiro de 2023: Jan a Nov completos (11) + 20 dias em Dez (1) = 12
    assert res.decimo_terceiro == Decimal("2400.00")


def test_salario_limite_minimo():
    # Deve aceitar exatamente 1.00 ou mais
    res = calcular_beneficios_rescisao(
        salario=Decimal("1.00"),
        data_admissao=date(2023, 1, 1),
        data_demissao=date(2023, 12, 31),
    )
    assert res.total > 0


def test_salario_abaixo_do_permitido():
    # Menor que 1.00 deve falhar
    with pytest.raises(ValueError, match=r"superior a R\$ 1,00"):
        calcular_beneficios_rescisao(
            salario=Decimal("0.99"),
            data_admissao=date(2023, 1, 1),
            data_demissao=date(2023, 12, 31),
        )


def test_decimo_terceiro_mesmo_mes_e_ano_suficiente():
    # Admissão e demissão no mesmo mês/ano com >= 15 dias: deve contar 1 mês
    # 01/06 a 15/06 = 15 dias (inclusive) -> 1/12 avos
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2023, 6, 1),
        data_demissao=date(2023, 6, 15),
    )
    assert res.decimo_terceiro == Decimal("200.00")  # 1/12


def test_decimo_terceiro_mesmo_mes_e_ano_insuficiente():
    # Admissão e demissão no mesmo mês/ano com < 15 dias: deve contar 0 meses
    # 01/06 a 14/06 = 14 dias (inclusive) -> 0 avos
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2023, 6, 1),
        data_demissao=date(2023, 6, 14),
    )
    assert res.decimo_terceiro == Decimal("0.00")


def test_ferias_demissao_no_aniversario_exato():
    # Demitido no dia exato do aniversário de admissão:
    # No novo modelo, exatamente no aniversário o ciclo reseta para 0 avos
    # pois o período anterior tornou-se "vencido".
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2022, 6, 1),
        data_demissao=date(2023, 6, 1),
    )
    assert res.ferias_proporcionais == Decimal("0.00")


def test_arredondamento_salario_nao_divisivel():
    # 2500 / 12 = 208.333... -> arredonda para 208.33 (ROUND_HALF_UP)
    res = calcular_beneficios_rescisao(
        salario=Decimal("2500.00"),
        data_admissao=date(2023, 1, 1),
        data_demissao=date(2023, 1, 31),
    )
    assert res.decimo_terceiro == Decimal("208.33")


def test_salario_tipo_errado():
    with pytest.raises(TypeError, match="O salário deve ser do tipo Decimal"):
        calcular_beneficios_rescisao(
            salario="2400.00",  # type: ignore
            data_admissao=date(2023, 1, 1),
            data_demissao=date(2023, 12, 31),
        )


def test_datas_tipo_errado():
    with pytest.raises(TypeError, match="deve ser do tipo date"):
        calcular_beneficios_rescisao(
            salario=Decimal("3000.00"),
            data_admissao="2023-01-01",  # type: ignore
            data_demissao=date(2023, 12, 31),
        )


def test_data_fora_do_range():
    with pytest.raises(ValueError, match="fora do intervalo permitido"):
        calcular_beneficios_rescisao(
            salario=Decimal("3000.00"),
            data_admissao=date(1899, 12, 31),
            data_demissao=date(2023, 12, 31),
        )


def test_decimo_terceiro_virada_de_ano():
    # Demissão em 31/12: 13º inclui nov (16 dias) + dez = 2 meses
    res_antes = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2022, 11, 15),
        data_demissao=date(2022, 12, 31),
    )
    assert res_antes.decimo_terceiro == Decimal("400.00")  # 2/12

    # Demissão em 01/01/2023: 13º de 2023 zera (jan tem 1 dia < 15)
    res_depois = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2022, 11, 15),
        data_demissao=date(2023, 1, 1),
    )
    assert res_depois.decimo_terceiro == Decimal("0.00")


def test_ferias_um_dia_antes_aniversario():
    # Admissão 15/05/2022, demissão 14/05/2023 (1 dia antes do aniversário)
    res = calcular_beneficios_rescisao(
        salario=Decimal("2400.00"),
        data_admissao=date(2022, 5, 15),
        data_demissao=date(2023, 5, 14),
    )
    assert res.ferias_proporcionais == Decimal("2400.00")  # 12/12


def test_decimo_terceiro_janeiro_proximo_ano_sem_duplicidade():
    """Garante que demissões em Janeiro não contem o mês duas vezes."""
    res = calcular_beneficios_rescisao(
        salario=Decimal("1200.00"),
        data_admissao=date(2022, 1, 1),
        data_demissao=date(2023, 1, 20),
    )
    assert res.decimo_terceiro == Decimal("100.00")


def test_ferias_aniversario_29_fevereiro():
    # Admitido 29/02/2020. Demitido 15/03/2023 (ano não bissexto).
    # O código deve ajustar o aniversário para 28/02/2023.
    res = calcular_beneficios_rescisao(
        salario=Decimal("1200.00"),
        data_admissao=date(2020, 2, 29),
        data_demissao=date(2023, 3, 15),
    )
    assert res.ferias_proporcionais == Decimal("100.00") # 1/12


def test_ferias_mes_curto_no_aniversario():
    # Admitido 31/01/2023. Demitido 31/03/2023.
    # 31/01 a 28/02 (ou 02/03?) -> 1 mês.
    # 01/03 a 31/03 -> 1 mês.
    # Total = 2 meses.
    res = calcular_beneficios_rescisao(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 1, 31),
        data_demissao=date(2023, 3, 31),
    )
    assert res.ferias_proporcionais == Decimal("200.00") # 2/12


def test_data_limites_invalidos_extras():
    """Valida erro para datas fora do range 1900-2100 (extras)."""
    with pytest.raises(ValueError, match="fora do intervalo permitido"):
        calcular_beneficios_rescisao(
            salario=Decimal("2000"),
            data_admissao=date(2023, 1, 1),
            data_demissao=date(2101, 1, 1),
        )


def test_salario_limites_extremos_extras():
    """Valida erro para salários fora da faixa permitida (extras)."""
    with pytest.raises(ValueError, match="acima do limite permitido"):
        calcular_beneficios_rescisao(
            salario=Decimal("1000001.00"),
            data_admissao=date(2023, 1, 1),
            data_demissao=date(2023, 12, 31),
        )


def test_ferias_proporcionais_varios_anos_extras():
    """Valida cálculo de férias proporcionais após vários anos de contrato."""
    # Admitido 10/05/2020. Demitido 25/06/2023. -> 2 meses no ciclo atual.
    res = calcular_beneficios_rescisao(
        salario=Decimal("1200.00"),
        data_admissao=date(2020, 5, 10),
        data_demissao=date(2023, 6, 25),
    )
    assert res.ferias_proporcionais == Decimal("200.00")


def test_ferias_aniversario_leap_year_cycle():
    # Admitido 29/02/2024. Demitido 01/01/2026.
    # Aniv 2026: 28/02 (não bissexto) > 01/01.
    # Ultimo aniv: 2025 (não bissexto) -> 28/02/2025.
    res = calcular_beneficios_rescisao(
        salario=Decimal("1200.00"),
        data_admissao=date(2024, 2, 29),
        data_demissao=date(2026, 1, 1),
    )
    # De 28/02/2025 até 01/01/2026: 10 meses.
    # 28/02 a 28/12 = 10 meses.
    # 28/12 a 01/01 = 4 dias. < 15. -> Total 10 meses.
    assert res.ferias_proporcionais == Decimal("1000.00")



def test_ferias_mes_boundary_adjustment():
    """Valida o ajuste de dia quando o mês destino é mais curto (ex: 31/01 -> 28/02)."""
    # Admitido 31/01/2023. Demitido 01/03/2023.
    # meses = 1.
    res = calcular_beneficios_rescisao(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 1, 31),
        data_demissao=date(2023, 3, 1),
    )
    assert res.ferias_proporcionais == Decimal("100.00")


def test_ferias_ciclo_fechado_mes_curto():
    """Valida que 31/01 a 28/02 fecha exatamente 1 mês."""
    res = calcular_beneficios_rescisao(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 1, 31),
        data_demissao=date(2023, 2, 28),
    )
    # Com a correção de usar ultimo_aniversario.day (28),
    # data_demissao.day (28) < 28 é falso.
    # meses = 1. dias_no_ultimo_mes = (28/02 - 28/02) + 1 = 1.
    # Total = 1 mês.
    assert res.ferias_proporcionais == Decimal("100.00")


def test_salario_exatamente_limite_maximo():
    # Deve aceitar exatamente 1.000.000,00
    res = calcular_beneficios_rescisao(
        salario=Decimal("1000000.00"),
        data_admissao=date(2023, 1, 1),
        data_demissao=date(2023, 12, 31),
    )
    assert res.decimo_terceiro == Decimal("1000000.00")


def test_dias_trabalhados_fevereiro_limiar():
    # Fevereiro (não bissexto) tem 28 dias.
    # 01/02 a 15/02 = 15 dias -> conta 1 mês
    res = calcular_decimo_terceiro(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 2, 1),
        data_demissao=date(2023, 2, 15),
    )
    assert res == Decimal("100.00")

    # 01/02 a 14/02 = 14 dias -> não conta
    res_neg = calcular_decimo_terceiro(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 2, 1),
        data_demissao=date(2023, 2, 14),
    )
    assert res_neg == Decimal("0.00")


def test_dias_trabalhados_fevereiro_bissexto_limiar():
    # Fevereiro (bissexto) tem 29 dias.
    # 01/02 a 15/02 = 15 dias -> conta 1 mês
    res = calcular_decimo_terceiro(
        salario=Decimal("1200.00"),
        data_admissao=date(2024, 2, 1),
        data_demissao=date(2024, 2, 15),
    )
    assert res == Decimal("100.00")


def test_dias_trabalhados_mes_30_dias_limiar():
    # Junho tem 30 dias.
    # 16/06 a 30/06 = 15 dias -> conta 1 mês
    res = calcular_decimo_terceiro(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 6, 16),
        data_demissao=date(2023, 6, 30),
    )
    assert res == Decimal("100.00")

    # 17/06 a 30/06 = 14 dias -> não conta
    res_neg = calcular_decimo_terceiro(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 6, 17),
        data_demissao=date(2023, 6, 30),
    )
    assert res_neg == Decimal("0.00")


def test_decimo_terceiro_admissao_tardia_no_mes():
    # Admissão: 20/01. Demissão: 20/02.
    # Jan: 20 a 31 = 12 dias -> não conta
    # Fev: 01 a 20 = 20 dias -> conta
    # Total: 1 mês
    res = calcular_decimo_terceiro(
        salario=Decimal("1200.00"),
        data_admissao=date(2023, 1, 20),
        data_demissao=date(2023, 2, 20),
    )
    assert res == Decimal("100.00")


def test_decimo_terceiro_limiar_fevereiro_bissexto_real():
    # Admissão: 29/02/2024. Demissão: 15/03/2024.
    # Fev: 29 a 29 = 1 dia -> não conta
    # Mar: 01 a 15 = 15 dias -> conta
    # Total: 1 mês
    res = calcular_decimo_terceiro(
        salario=Decimal("1200.00"),
        data_admissao=date(2024, 2, 29),
        data_demissao=date(2024, 3, 15),
    )
    assert res == Decimal("100.00")
