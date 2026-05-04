from src.uis.validators import (
    MAX_CASAS,
    MAX_POSICAO,
    MIN_CASAS,
    MIN_POSICAO,
    ValidationError,
)


def validar_posicao(valor: object) -> int:
    """Inteiro 1..10_000_000. (Obrigatório)"""
    if valor is None or valor == "":
        raise ValidationError("Por favor, insira um número.")
    try:
        n = int(str(valor))
    except (TypeError, ValueError):
        raise ValidationError("Posição deve ser um número inteiro.")
    if n < MIN_POSICAO:
        raise ValidationError(
            f"O valor '{n}' não pode ser aceito. "
            f"O valor mínimo permitido é {MIN_POSICAO}."
        )
    if n > MAX_POSICAO:
        raise ValidationError(
            f"Posição muito alta. O valor máximo permitido é {MAX_POSICAO}."
        )
    return n


def validar_casas(valor: object) -> int:
    """Inteiro 3..999. (Obrigatório)"""
    if valor is None or valor == "":
        raise ValidationError("Por favor, insira o número de casas.")
    try:
        n = int(str(valor))
    except (TypeError, ValueError):
        raise ValidationError("Número de casas deve ser inteiro.")
    if n < MIN_CASAS or n > MAX_CASAS:
        raise ValidationError(
            f"Número de casas deve estar entre {MIN_CASAS} e {MAX_CASAS}."
        )
    return n
