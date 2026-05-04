from decimal import Decimal
from typing import Protocol

import httpx

from src.infra.logger import get_logger

logger = get_logger("SalarioAPI")


class ISalarioClient(Protocol):
    """Interface para o cliente de obtenção de salário."""

    async def obter_salario(self, estado: str) -> Decimal: ...


class HttpSalarioClient:
    """Implementação real HTTP que busca o salário da API do Banco Central."""

    def __init__(
        self, url_base: str, timeout: int = 5, client: httpx.AsyncClient | None = None
    ):
        self._url_base = url_base
        self._timeout = timeout
        self._client = client

    async def obter_salario(self, estado: str) -> Decimal:
        # Estados que possuem piso regional próprio não são cobertos pela API nacional
        estados_com_piso_proprio = ["SP", "RJ", "PR", "SC", "RS"]
        if estado in estados_com_piso_proprio:
            raise NotImplementedError(
                f"O estado {estado} possui piso regional próprio."
            )

        try:
            # Se um cliente foi injetado, usamos ele.
            # Caso contrário, criamos um efêmero com retries.
            if self._client:
                return await self._execute_request(self._client, estado)

            # Configuração de retries para maior resiliência em chamadas externas
            transport = httpx.AsyncHTTPTransport(retries=3)
            async with httpx.AsyncClient(
                timeout=self._timeout, transport=transport
            ) as client:
                return await self._execute_request(client, estado)

        except httpx.TimeoutException:
            logger.error(
                f"Timeout ao acessar API de Salário para {estado} após {self._timeout}s"
            )
            raise ConnectionError("Tempo esgotado ao conectar com a API do Governo.")
        except Exception as e:
            logger.warning(f"Erro na chamada à API para {estado}: {e}")
            raise ConnectionError("Falha técnica ao obter dados da API.")

    async def _execute_request(self, client: httpx.AsyncClient, estado: str) -> Decimal:
        """Executa a requisição HTTP e valida o payload de resposta."""
        response = await client.get(
            self._url_base, headers={"User-Agent": "Mozilla/5.0/e-DEPLOY-Tech-Lead"}
        )
        response.raise_for_status()

        data = response.json()
        if isinstance(data, list) and len(data) > 0 and "valor" in data[0]:
            valor_str = str(data[0]["valor"])
            return Decimal(valor_str)

        raise ValueError(
            "Formato de resposta da API inválido ou série histórica vazia."
        )
