from src.uis.validators import MAX_TEXTO_INPUT, ValidationError


def validar_texto(valor: object) -> str:
    """Texto não-vazio, com limite de tamanho. (Obrigatório)"""
    if valor is None or str(valor) == "":
        raise ValidationError("Por favor, insira um texto.")

    texto = str(valor)
    if len(texto) > MAX_TEXTO_INPUT:
        raise ValidationError(f"Texto muito longo (máx. {MAX_TEXTO_INPUT} caracteres).")
    return texto
