import pytest
from playwright.sync_api import Page, expect

# Importação das listas oficiais de casos de teste do domínio
from questoes.ex001_validacao_string.test_validacao_string import (
    CASOS_ESPECIAIS,
    CASOS_HOMOGLIFOS_INVALIDOS,
    CASOS_INVALIDOS_CASE,
    CASOS_INVALIDOS_CONTEUDO,
    CASOS_INVALIDOS_ESPACOS,
    CASOS_INVALIDOS_POSICAO,
    CASOS_LONGOS,
    CASOS_NULO_OU_VAZIO,
    CASOS_UNICODE_VALIDOS,
    CASOS_VALIDOS,
)

# --- Agrupamento dos casos conforme solicitado ---
LISTA_SUCESSO = (
    CASOS_VALIDOS + CASOS_ESPECIAIS + CASOS_UNICODE_VALIDOS + [CASOS_LONGOS[0]]
)

# Filtramos None pois não é possível digitar None no input HTML.
LISTA_ERRO = (
    CASOS_INVALIDOS_CASE
    + CASOS_INVALIDOS_POSICAO
    + CASOS_INVALIDOS_CONTEUDO
    + CASOS_INVALIDOS_ESPACOS
    + CASOS_HOMOGLIFOS_INVALIDOS
    + [c for c in CASOS_NULO_OU_VAZIO if c is not None]
)


@pytest.fixture(scope="function", autouse=True)
def setup_test(page: Page, base_url: str):
    """Navega para a tela do Exercício 1 antes de cada teste."""
    page.goto(f"{base_url}/exercicio-001")
    expect(page.locator("text=Entrada de Dados")).to_be_visible(timeout=30000)


@pytest.mark.parametrize("entrada", LISTA_SUCESSO)
def test_ui_validacao_sucesso(page: Page, entrada):
    """
    Teste de Sucesso: Valida cada entrada que deve ser considerada VÁLIDA.
    Utiliza a sequência de finalização do botão (limpeza) para fluidez.
    """
    input_field = page.locator('input[aria-label="Texto para validar"]')

    # Preenche e dispara
    input_field.fill(str(entrada))
    page.keyboard.press("Enter")

    # Ação sequencial: Aguarda o input ser limpo (final da ação do botão)
    expect(input_field).to_have_value("", timeout=3000)

    # Valida o resultado no topo do histórico
    expect(page.locator("div.q-badge:has-text('VÁLIDO')").first).to_be_visible()


@pytest.mark.parametrize("entrada", LISTA_ERRO)
def test_ui_validacao_erro(page: Page, entrada):
    """
    Teste de Erro: Valida cada entrada que deve ser considerada INVÁLIDA.
    """
    input_field = page.locator('input[aria-label="Texto para validar"]')

    # Preenche e dispara
    input_field.fill(str(entrada))
    page.keyboard.press("Enter")

    if entrada == "":
        # Erro de validação de campo vazio (Regra da UI)
        expect(page.get_by_text("Por favor, insira um texto")).to_be_visible()
    else:
        # Erro de lógica de negócio (INVÁLIDO)
        expect(input_field).to_have_value("", timeout=3000)
        expect(page.locator("div.q-badge:has-text('INVÁLIDO')").first).to_be_visible()


# --- Testes de Comportamento de Componentes ---


def test_component_autofocus(page: Page):
    """Valida foco automático ao carregar (setup_focus)."""
    input_field = page.locator('input[aria-label="Texto para validar"]')
    # Aguarda o timer de foco definido no app.py (0.3s) + margem
    page.wait_for_timeout(600)
    expect(input_field).to_be_focused()


def test_component_button_visuals(page: Page):
    """Valida se o botão 'Executar' possui o ícone 'bolt' e estilo esperado."""
    btn = page.locator('button:has-text("Executar")')
    expect(btn).to_be_visible()
    # Verifica presença do ícone de raio (Material Design 'bolt')
    expect(btn.locator("i:has-text('bolt')")).to_be_visible()


def test_component_input_constraints(page: Page):
    """Valida se o campo de input respeita o limite de caracteres definido."""
    input_field = page.locator('input[aria-label="Texto para validar"]')
    expect(input_field).to_have_attribute("maxlength", "1000")


def test_component_history_stacking_order(page: Page):
    """Valida se o histórico exibe o item mais recente no topo (flex-col-reverse)."""
    input_field = page.locator('input[aria-label="Texto para validar"]')

    # Executa duas validações distintas
    entradas = ["BOLA", "BANANA"]
    for entrada in entradas:
        input_field.fill(entrada)
        page.keyboard.press("Enter")
        expect(input_field).to_have_value("")

    # O primeiro elemento renderizado no histórico deve ser o último inserido ("BANANA")
    # Em flex-col-reverse, o último no DOM é o primeiro no topo visual
    resultado_recente = page.locator(".font-mono.text-primary").last
    expect(resultado_recente).to_have_text('"BANANA"', timeout=10000)
