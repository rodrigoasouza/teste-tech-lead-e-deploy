"""
Validadores de borda da UI.

Regra: as telas NÃO contêm regra de negócio. Elas apenas:
  - validam o que ENTRA (tipo, faixa, formato, tamanho);
  - normalizam para um tipo seguro antes de enviar ao serviço;
  - validam/sanitizam o que SAI (limites de tamanho ao renderizar).

Toda função levanta `ValidationError` com mensagem segura para exibir ao usuário.
Erros internos (do serviço) NÃO devem ser propagados ao usuário cru.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Final

# Limites defensivos contra abuso (DoS / payload-bomb)
MAX_TEXTO_INPUT: Final[int] = 1_000
MIN_POSICAO: Final[int] = 1
MAX_POSICAO: Final[int] = 10_000_000
MIN_CASAS: Final[int] = 3
MAX_CASAS: Final[int] = 999
MAX_SALARIO: Final[Decimal] = Decimal("1000000.00")


class ValidationError(ValueError):
    """Erro de validação de input — mensagem segura para o usuário."""
