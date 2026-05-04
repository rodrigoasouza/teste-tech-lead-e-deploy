from datetime import datetime

from nicegui import ui

from questoes.ex002_sequencia_numerica.sequencia_numerica import (
    calcular_valor_sequencia,
)
from src.infra.logger import get_logger
from src.uis.components.button import BotaoExecutarPadrao
from src.uis.validators import ValidationError

from .validators import validar_posicao

logger = get_logger("Ex02_Sequencia")

METADATA = {
    "id": 2,
    "title": "Sequência Numérica",
    "icon": "show_chart",
    "description": "Calcula progressão aritmética dinâmica.",
    "color": "#3fb950",
}


def render(setup_page, setup_focus):
    setup_page()
    with ui.column().classes("w-full max-w-4xl mx-auto p-12 gap-8"):
        with ui.column().classes("gap-1"):
            with ui.row().classes("items-center gap-4"):
                ui.icon(METADATA["icon"]).classes("text-4xl").style(
                    f"color: {METADATA['color']}"
                )
                ui.label(METADATA["title"]).classes("text-3xl font-bold")
            ui.label(METADATA["description"]).classes("text-slate-400 text-lg")

        with ui.card().classes("custom-card w-full"):
            ui.label("Parâmetros").classes(
                "text-sm font-bold text-slate-400 uppercase tracking-widest mb-2"
            )
            pos_input = (
                ui.input("Posição (N)", value=None, placeholder="Ex: 5")
                .classes("w-full")
                .props('outlined rounded type="number" no-stepper min="1"')
            )
            calc_btn = BotaoExecutarPadrao(
                on_clear=lambda: [
                    pos_input.set_value(None),
                    pos_input.run_method("focus"),
                ]
            )

        ui.label("Histórico de Execução").classes("text-lg font-bold mt-4")
        with ui.column().classes("history-table w-full p-0"):
            with ui.row().classes("history-header w-full justify-between items-center"):
                ui.label("Resultado da Sequência")
                with ui.row().classes("gap-8 items-center"):
                    ui.label("Visualização")
                    ui.label("Hora")

            results_container = ui.column().classes("w-full flex-col-reverse p-0")

        # Estado local para gerenciar o gráfico dinâmico
        state = {"max_val": 0, "rows": []}

        def run_sequence():
            try:
                n = validar_posicao(pos_input.value)
            except ValidationError as ve:
                ui.notify(str(ve), type="warning")
                pos_input.set_value(None)
                pos_input.run_method("focus")
                return

            try:
                val = calcular_valor_sequencia(n)
            except Exception:
                logger.error("Erro no cálculo de sequência", exc_info=True)
                ui.notify("Não foi possível calcular a sequência.", type="negative")
                return

            if not isinstance(val, int):
                logger.error("Saída inesperada do serviço: %r", type(val).__name__)
                ui.notify("Resposta inválida do serviço.", type="negative")
                return

            ui.notify(f"Calculado: {val}", type="positive")

            # Atualiza o valor máximo para escala do gráfico
            if val > state["max_val"]:
                state["max_val"] = val
                # Re-escala todas as barras existentes para manter a proporção
                for row in state["rows"]:
                    new_width = (row["val"] / state["max_val"]) * 100
                    row["bar"].style(f"width: {new_width}%")

            # Calcula largura proporcional (mínimo 1% para visibilidade)
            width = (
                max((val / state["max_val"] * 100), 1) if state["max_val"] > 0 else 100
            )
            now = datetime.now().strftime("%H:%M:%S")

            with results_container:
                # Layout melhorado com barra horizontal dinâmica
                with ui.column().classes(
                    "history-row animate-fade-in w-full gap-2 p-4"
                ):
                    with ui.row().classes("w-full justify-between items-end"):
                        with ui.column().classes("gap-0"):
                            ui.label(f"Posição {n}").classes(
                                "text-xs font-bold ed-muted uppercase tracking-wider"
                            )
                            ui.label(f"{val:,}".replace(",", ".")).classes(
                                "text-lg font-black text-primary leading-none"
                            )

                    # Container da barra
                    bar_container = ui.element("div").classes(
                        "w-full h-2.5 bg-slate-100 rounded-full overflow-hidden "
                        "relative border border-slate-200/50"
                    )
                    with bar_container:
                        bar = (
                            ui.element("div")
                            .classes("h-full transition-all duration-700 ease-out")
                            .style(
                                f"width: {width}%; "
                                f"background: linear-gradient(90deg, "
                                f"{METADATA['color']} 0%, "
                                f"{METADATA['color']}aa 100%);"
                            )
                        )

                    ui.label(now).classes(
                        "text-xs text-slate-400 font-mono "
                        "whitespace-nowrap self-center mt-1"
                    )

                # Salva referência para atualizações futuras
                state["rows"].append({"val": val, "bar": bar})

            pos_input.run_method("focus")

        calc_btn.on_click(run_sequence)

        setup_focus(pos_input)
