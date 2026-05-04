"""Cálculo de Férias e Décimo Terceiro proporcional para rescisão."""

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Final

MESES_ANO: Final[int] = 12
DIAS_MINIMOS_MES: Final[int] = 15
PRECISAO_MONETARIA: Final[Decimal] = Decimal("0.01")

@dataclass
class BeneficiosRescisao:
    """Representa os valores devidos na rescisão."""

    decimo_terceiro: Decimal
    ferias_proporcionais: Decimal

    @property
    def total(self) -> Decimal:
        """Valor total dos benefícios calculados."""
        return self.decimo_terceiro + self.ferias_proporcionais


def calcular_decimo_terceiro(
    salario: Decimal, data_admissao: date, data_demissao: date
) -> Decimal:
    """Calcula o 13º salário proporcional usando interseção de datas por mês."""
    ano_demissao = data_demissao.year
    meses_direito = 0

    # Avaliamos cada mês do ano da demissão de forma isolada
    for mes in range(1, 13):
        # Janela do mês no calendário
        _, ultimo_dia_mes = calendar.monthrange(ano_demissao, mes)
        inicio_mes = date(ano_demissao, mes, 1)
        fim_mes = date(ano_demissao, mes, ultimo_dia_mes)

        # Interseção real trabalhada dentro deste mês específico
        inicio_real = max(data_admissao, inicio_mes)
        fim_real = min(data_demissao, fim_mes)

        # Se houve intersecção válida entre o contrato e o mês
        if inicio_real <= fim_real:
            dias_no_mes = (fim_real - inicio_real).days + 1
            if dias_no_mes >= DIAS_MINIMOS_MES:
                meses_direito += 1

    return (salario * Decimal(meses_direito)) / Decimal(MESES_ANO)


def calcular_ferias_proporcionais(
    salario: Decimal, data_admissao: date, data_demissao: date
) -> Decimal:
    """Calcula férias proporcionais em ciclos de 12 meses (regra dos 15 dias)."""
    def _get_data_ciclo(ano: int, mes: int) -> date:
        """Retorna a data do ciclo ajustada para o último dia do mês."""
        _, ultimo_dia = calendar.monthrange(ano, mes)
        return date(ano, mes, min(data_admissao.day, ultimo_dia))

    aniversario_ano_demissao = _get_data_ciclo(
        data_demissao.year, data_admissao.month
    )

    if aniversario_ano_demissao > data_demissao:
        ultimo_aniversario = _get_data_ciclo(
            data_demissao.year - 1, data_admissao.month
        )
    else:
        ultimo_aniversario = aniversario_ano_demissao

    # Contagem de meses inteiros desde o último aniversário
    meses = (data_demissao.year - ultimo_aniversario.year) * 12 + (
        data_demissao.month - ultimo_aniversario.month
    )

    # Se o dia da demissão for anterior ao dia do aniversário, o mês não fechou
    if data_demissao.day < ultimo_aniversario.day:
        meses -= 1

    def _avancar_meses(n_meses: int) -> date:
        extra_anos = (ultimo_aniversario.month + n_meses - 1) // 12
        ano_alvo = ultimo_aniversario.year + extra_anos
        mes_alvo = (ultimo_aniversario.month + n_meses - 1) % 12 + 1
        return _get_data_ciclo(ano_alvo, mes_alvo)

    # Cálculo da fração do mês incompleto
    inicio_mes_incompleto = _avancar_meses(meses)
    dias_no_ultimo_mes = (data_demissao - inicio_mes_incompleto).days + 1

    if dias_no_ultimo_mes >= DIAS_MINIMOS_MES:
        meses += 1

    # Limite de 12/12 avos por ciclo
    meses_direito = min(MESES_ANO, meses)

    return (salario * Decimal(meses_direito)) / Decimal(MESES_ANO)


def calcular_beneficios_rescisao(
    salario: Decimal,
    data_admissao: date,
    data_demissao: date,
) -> BeneficiosRescisao:
    """Calcula Férias e Décimo Terceiro devidos na rescisão."""
    if not isinstance(salario, Decimal):
        raise TypeError("O salário deve ser do tipo Decimal.")

    if not isinstance(data_admissao, date) or not isinstance(data_demissao, date):
        raise TypeError("A data deve ser do tipo date.")

    if data_admissao.year < 1900 or data_demissao.year > 2100:
        raise ValueError("Datas fora do intervalo permitido (1900-2100).")

    if salario < Decimal("1.0"):
        raise ValueError("O salário deve ser superior a R$ 1,00.")

    if salario > Decimal("1000000.00"):
        raise ValueError("Salário acima do limite permitido (R$ 1.000.000,00).")

    if data_demissao < data_admissao:
        raise ValueError("A data de demissão não pode ser anterior à data de admissão.")

    decimo_terceiro = calcular_decimo_terceiro(salario, data_admissao, data_demissao)
    ferias = calcular_ferias_proporcionais(salario, data_admissao, data_demissao)

    return BeneficiosRescisao(
        decimo_terceiro=decimo_terceiro.quantize(
            PRECISAO_MONETARIA, rounding=ROUND_HALF_UP
        ),
        ferias_proporcionais=ferias.quantize(
            PRECISAO_MONETARIA, rounding=ROUND_HALF_UP
        ),
    )
