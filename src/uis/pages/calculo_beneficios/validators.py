from decimal import Decimal, InvalidOperation

from src.uis.validators import MAX_SALARIO, ValidationError


def validar_salario(valor: object) -> Decimal:
    """Valor monetário igual ou superior a R$ 1,00. (Obrigatório)"""
    if valor is None or valor == "":
        raise ValidationError("Informe o salário.")
    try:
        dec = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Salário inválido.")
    if dec < 1:
        raise ValidationError("O salário deve ser no mínimo R$ 1,00.")
    if dec > MAX_SALARIO:
        raise ValidationError("Salário acima do limite permitido.")
    return dec
