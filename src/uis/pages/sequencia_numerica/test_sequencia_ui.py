import pytest
from playwright.sync_api import Page, expect

# Importação dos dados de teste oficiais do Exercício 2
from questoes.ex002_sequencia_numerica.test_sequencia_numerica import (
    POSICOES_INVALIDAS,
    VALORES_DO_ENUNCIADO,
)


@pytest.fixture(scope="function", autouse=True)
def setup_test(page: Page, base_url: str):
    """Navega para a tela do Exercício 2 antes de cada teste."""
    page.goto(f"{base_url}/exercicio-002")
    expect(page.locator("text=Sequência Numérica")).to_be_visible()


@pytest.mark.parametrize("posicao, esperado", VALORES_DO_ENUNCIADO[:4])
def test_ui_sequencia_sucesso(page: Page, posicao, esperado):
    """Valida o cálculo correto da sequência via interface."""
    input_field = page.locator('input[aria-label="Posição (N)"]')

    # Preenche a posição
    input_field.fill(str(posicao))
    page.keyboard.press("Enter")

    # Aguarda o reset do campo para vazio (após execução)
    expect(input_field).to_have_value("", timeout=5000)

    # Valida se o resultado apareceu no histórico
    # A UI renderiza posição e valor em labels separadas,
    # com separador de milhar (ponto)
    expect(page.locator(f"text=Posição {posicao}").first).to_be_visible()
    formatted = f"{esperado:,}".replace(",", ".")
    expect(page.locator(f"text={formatted}").first).to_be_visible()


@pytest.mark.parametrize("posicao", POSICOES_INVALIDAS)
def test_ui_sequencia_erro_validacao_limites(page: Page, posicao):
    """Valida se valores fora da faixa (0 ou menos) disparam erro."""
    input_field = page.locator('input[aria-label="Posição (N)"]')

    input_field.fill(str(posicao))
    page.keyboard.press("Enter")

    # Valida notificação de erro de limites
    expect(
        page.locator(
            "div.q-notification:has-text('não pode ser aceito. "
            "O valor mínimo permitido é 1')"
        )
    ).to_be_visible()


def test_ui_sequencia_erro_vazio(page: Page):
    """Valida se clicar sem preencher nada dispara o erro de obrigatoriedade."""
    input_field = page.locator('input[aria-label="Posição (N)"]')

    # Garante que está vazio
    expect(input_field).to_have_value("")

    # Tenta executar
    page.get_by_role("button", name="Executar").click()

    # Valida notificação de erro de campo obrigatório
    expect(
        page.locator("div.q-notification:has-text('Por favor, insira um número.')")
    ).to_be_visible()


# --- Testes de Comportamento de Componentes ---


def test_component_autofocus(page: Page):
    """Valida que o campo de posição recebe foco automaticamente."""
    input_field = page.locator('input[aria-label="Posição (N)"]')
    # Aguarda o timer de foco (0.3s)
    page.wait_for_timeout(600)
    expect(input_field).to_be_focused()


def test_component_button_icon(page: Page):
    """Valida a presença do ícone 'bolt' no botão de execução."""
    btn = page.locator('button:has-text("Executar")')
    expect(btn.locator("i:has-text('bolt')")).to_be_visible()


def test_component_history_reverse_order(page: Page):
    """Valida se os cálculos recentes aparecem no topo do histórico."""
    input_field = page.locator('input[aria-label="Posição (N)"]')

    # Executa Posição 1 e depois Posição 2
    for n in [1, 2]:
        input_field.fill(str(n))
        page.keyboard.press("Enter")
        expect(input_field).to_have_value("")

    # O primeiro item no histórico deve ser a Posição 2
    # Em flex-col-reverse, o topo visual é o último no DOM
    resultado_recente = page.locator(".history-row").last
    expect(resultado_recente.locator("text=Posição 2")).to_be_visible(timeout=10000)
