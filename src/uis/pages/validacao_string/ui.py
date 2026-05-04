from datetime import datetime

from nicegui import ui

# Geralmente business logic fica em src/services, mas as questões originais
# estavam em pastas separadas. Vou manter a referência original por enquanto.
from questoes.ex001_validacao_string.validacao_string import (
    verificar_com_metodos_string,
)
from src.infra.logger import get_logger
from src.uis.components.button import BotaoExecutarPadrao
from src.uis.validators import (
    ValidationError,
)

from .validators import validar_texto

logger = get_logger("Ex01_Validacao")

METADATA = {
    "id": 1,
    "title": "Validação de String",
    "icon": "abc",
    "description": "Verifica se a string começa com B e termina com A.",
    "color": "#a371f7",
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
            ui.label("Entrada de Dados").classes(
                "text-sm font-bold text-slate-400 uppercase tracking-widest mb-2"
            )
            input_text = (
                ui.input("Texto para validar", placeholder="Ex: BANANA")
                .classes("w-full")
                .props("outlined rounded maxlength=1000")
            )

            process_btn = BotaoExecutarPadrao(
                on_clear=lambda: [
                    input_text.set_value(""),
                    input_text.run_method("focus"),
                ]
            )

        ui.label("Histórico de Execuções").classes("text-lg font-bold mt-4")
        with ui.column().classes("history-table w-full p-0"):
            with ui.row().classes("history-header w-full justify-between items-center"):
                ui.label("Entrada")
                with ui.row().classes("gap-8 items-center"):
                    ui.label("Status")
                    ui.label("Hora")

            results_container = ui.column().classes("w-full flex-col-reverse p-0")

        def run_validation():
            try:
                texto = validar_texto(input_text.value)
            except ValidationError as ve:
                ui.notify(str(ve), type="warning")
                input_text.run_method("focus")
                return

            try:
                res = verificar_com_metodos_string(texto)
            except Exception:
                logger.error("Erro na execução do serviço de validação", exc_info=True)
                ui.notify("Não foi possível processar a validação.", type="negative")
                input_text.run_method("focus")
                return

            if not isinstance(res, bool):
                logger.error("Saída inesperada do serviço: %r", type(res).__name__)
                ui.notify("Resposta inválida do serviço.", type="negative")
                input_text.run_method("focus")
                return

            status = "VÁLIDO" if res else "INVÁLIDO"
            color = "positive" if res else "negative"
            full_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            ui.notify(f"Processado: {status}", type=color)

            with results_container:
                with ui.row().classes("history-row animate-fade-in"):
                    with ui.row().classes(
                        "items-center gap-4 flex-grow overflow-hidden"
                    ):
                        with ui.column().classes("gap-1 flex-grow overflow-hidden"):
                            # Lógica para colorir os caracteres de decisão (B...A)
                            # B (Início) e A (Fim) em verde se corretos,
                            # vermelho se não.
                            def get_colored_html(t):
                                if not t:
                                    return '""'
                                f_char = t[0]
                                l_char = t[-1] if len(t) > 1 else None

                                f_color = "#3fb950" if f_char == "B" else "#f85149"
                                res_html = (
                                    f'<span style="color:{f_color}; font-weight:900">'
                                    f"{f_char}</span>"
                                )

                                if l_char is not None:
                                    middle = t[1:-1]
                                    l_color = "#3fb950" if l_char == "A" else "#f85149"
                                    res_html += f"<span>{middle}</span>"
                                    res_html += (
                                        f'<span style="color:{l_color}; '
                                        f'font-weight:900">{l_char}</span>'
                                    )

                                return (
                                    f'<div class="font-mono text-primary text-base '
                                    f'font-bold break-all">"{res_html}"</div>'
                                )

                            with ui.row().classes("items-center gap-6"):
                                with ui.column().classes("gap-1"):
                                    ui.html(get_colored_html(texto))
                                    ui.badge(
                                        status, color="green" if res else "red"
                                    ).classes("w-fit")

                                ui.label(full_date).classes(
                                    "text-xs text-slate-400 font-mono "
                                    "whitespace-nowrap self-center"
                                )

            input_text.run_method("focus")

        process_btn.on_click(run_validation)

        setup_focus(input_text)
