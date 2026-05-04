import re

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function", autouse=True)
def setup_test(page: Page, base_url: str):
    """Navega para a tela do Exercício 3 antes de cada teste."""
    page.goto(f"{base_url}/exercicio-003")
    expect(page.locator("text=Jogo de Tabuleiro")).to_be_visible(timeout=15000)


def test_ui_tabuleiro_sucesso_imediato(page: Page):
    """Valida que o resultado aparece imediatamente e o campo limpa."""
    input_field = page.locator('input[aria-label="Número de Casas"]')

    input_field.fill("10")
    page.keyboard.press("Enter")

    # 1. Deve limpar o campo imediatamente
    expect(input_field).to_have_value("")

    # 2. O resultado deve aparecer no histórico (não deve esperar os 5s da roleta)
    expect(page.locator("text=Casas: 10").first).to_be_visible()
    expect(page.locator("text=Probabilidade: 3.704%")).to_be_visible()


def test_ui_tabuleiro_probabilidade_3_casas(page: Page):
    """Valida a formatação de 3 casas decimais na probabilidade."""
    input_field = page.locator('input[aria-label="Número de Casas"]')

    # 5 casas -> distância 4 -> turnos 2 -> prob 3/9 (33.333%)
    input_field.fill("5")
    page.get_by_role("button", name="Executar").click()

    expect(page.locator("text=Probabilidade: 33.333%")).to_be_visible()


def test_ui_tabuleiro_animacao_roleta_reset(page: Page):
    """Valida que a roleta inicia animação e persiste ao clicar novamente."""
    input_field = page.locator('input[aria-label="Número de Casas"]')
    roulette = page.locator("#roulette-wheel")

    input_field.fill("10")
    page.get_by_role("button", name="Executar").click()

    # Deve estar girando (tem a classe spinning-wheel)
    expect(roulette).to_have_class(re.compile(r"spinning-wheel"))

    # Clica de novo após 2 segundos
    page.wait_for_timeout(2000)
    input_field.fill("15")
    page.get_by_role("button", name="Executar").click()

    # Deve continuar girando (resetou o timer)
    expect(roulette).to_have_class(re.compile(r"spinning-wheel"))

    # Aguarda mais 4 segundos (total 6 desde o primeiro clique, mas 4 desde o segundo)
    # Ainda deve estar girando pois o timer é de 5s desde o último clique
    page.wait_for_timeout(3000)
    expect(roulette).to_have_class(re.compile(r"spinning-wheel"))

    # Aguarda mais 3 segundos (total 7 desde o segundo clique)
    # Agora deve ter parado
    page.wait_for_timeout(3000)
    expect(roulette).not_to_have_class(re.compile(r"spinning-wheel"))
    expect(page.locator(".roulette-number")).to_have_text(re.compile(r"[123]"))


def test_ui_tabuleiro_erro_validacao_limpa_campo(page: Page):
    """Valida que valores menores que 3 disparam erro e limpam o campo."""
    input_field = page.locator('input[aria-label="Número de Casas"]')

    input_field.fill("2")
    page.get_by_role("button", name="Executar").click()

    # Valida notificação de erro
    expect(
        page.locator(
            "div.q-notification:has-text('Número de casas deve estar entre 3 e 999')"
        )
    ).to_be_visible()

    # Campo deve ter sido limpo
    expect(input_field).to_have_value("")
