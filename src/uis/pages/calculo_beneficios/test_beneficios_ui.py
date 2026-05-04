import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function", autouse=True)
def setup_test(page: Page, base_url: str):
    """Navega para a tela do Exercício 4 antes de cada teste."""
    page.goto(f"{base_url}/exercicio-004")
    expect(page.locator("text=Calculadora de Benefícios")).to_be_visible()


def test_ui_calculo_sucesso_simplificado(page: Page):
    """Valida o cálculo simplificado sem dependência de estado."""
    # Preenche Salário Base (R$ 3.000,00)
    sal_input = page.locator('input[aria-label="Salário Base"]')
    sal_input.fill("3000")

    # Preenche Datas (1 ano cheio)
    page.locator('input[aria-label="Admissão"]').fill("01/01/2023")
    page.locator('input[aria-label="Demissão"]').fill("31/12/2023")

    # Executa via teclado
    page.keyboard.press("Enter")

    # Valida se os resultados apareceram no histórico
    # 3000 (13º) + 3000 (Férias) = 6000
    expect(page.locator("text=R$ 6,000.00").last).to_be_visible(timeout=10000)
    expect(page.locator("text=13º Salário:").last).to_be_visible()
    expect(page.locator("text=R$ 3,000.00").last).to_be_visible()

    # Valida a limpeza dos campos
    expect(sal_input).to_have_value("")
    expect(page.locator('input[aria-label="Admissão"]')).to_have_value("__/__/____")
    expect(page.locator('input[aria-label="Demissão"]')).to_have_value("__/__/____")


def test_ui_erro_salario_abaixo_minimo_simples(page: Page):
    """Valida erro quando o salário é <= 1.00."""
    sal_input = page.locator('input[aria-label="Salário Base"]')
    sal_input.fill("0.50")
    page.keyboard.press("Enter")

    # Usando match ainda mais simples para evitar problemas de formatação do R$
    expect(page.get_by_text("1,00")).to_be_visible()


def test_ui_erro_periodo_invalido(page: Page):
    """Valida erro de demissão anterior à admissão."""
    # Preenche um salário válido para que o validador de datas seja alcançado
    page.locator('input[aria-label="Salário Base"]').fill("3000")
    page.locator('input[aria-label="Admissão"]').fill("01/01/2024")
    page.locator('input[aria-label="Demissão"]').fill("01/01/2023")
    page.keyboard.press("Enter")
    page.wait_for_timeout(1000)

    # Espera a notificação do Quasar (NiceGUI usa Quasar)
    expect(page.locator(".q-notification").last).to_contain_text("anterior")


def test_component_autofocus(page: Page):
    """Valida foco automático no campo de salário."""
    sal_input = page.locator('input[aria-label="Salário Base"]')
    page.wait_for_timeout(600)
    expect(sal_input).to_be_focused()
