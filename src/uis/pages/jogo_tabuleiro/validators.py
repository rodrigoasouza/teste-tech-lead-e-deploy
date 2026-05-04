from typing import Any

from src.uis.validators import MAX_CASAS, MIN_CASAS, ValidationError


def validar_casas(valor: Any) -> int:
    """Inteiro 3..999. (Obrigatório)"""
    if valor is None or valor == "":
        raise ValidationError("Por favor, insira o número de casas.")

    try:
        # Tenta converter para float primeiro (comum no NiceGUI ui.number)
        val_float = float(valor)
        # Verifica se é um número inteiro (ex: 10.0)
        if not val_float.is_integer():
            raise ValidationError("Número de casas deve ser um valor inteiro.")
        n = int(val_float)
    except (TypeError, ValueError):
        raise ValidationError("Número de casas inválido.")

    if n < MIN_CASAS or n > MAX_CASAS:
        raise ValidationError(
            f"Número de casas deve estar entre {MIN_CASAS} e {MAX_CASAS}."
        )
    return n
