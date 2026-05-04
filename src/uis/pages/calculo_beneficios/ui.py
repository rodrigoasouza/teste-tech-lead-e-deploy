from datetime import datetime

from nicegui import ui

from questoes.ex004_calculo_beneficios.calculo_beneficios import (
    calcular_beneficios_rescisao,
)
from src.infra.logger import get_logger
from src.uis.components.button import BotaoExecutarPadrao
from src.uis.components.date_input import DateRangePicker
from src.uis.validators import ValidationError

from .validators import validar_salario

logger = get_logger("Ex04_Beneficios")

METADATA = {
    "id": 4,
    "title": "Calculadora de Benefícios",
    "icon": "account_balance_wallet",
    "description": "Cálculo simplificado de 13º e Férias Proporcionais.",
    "color": "#f85149",
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

        with ui.card().classes("custom-card w-full gap-4"):
            sal_input = (
                ui.number(
                    "Salário Base",
                    value=None,
                    format="%.2f",
                    step=0.01,
                    precision=2,
                )
                .classes("w-full")
                .props('outlined rounded required-label placeholder="0,00"')
            )

            periodo = DateRangePicker(
                start_label="Admissão",
                end_label="Demissão",
                start_value="",
                end_value="",
                required=True,
            )

            def clear_inputs():
                sal_input.set_value(None)
                periodo.start_input.set_value("")
                periodo.end_input.set_value("")
                sal_input.run_method("focus")

            calc_btn = BotaoExecutarPadrao(on_clear=clear_inputs)

        ui.label("Histórico de Execução").classes("text-lg font-bold mt-4")
        with ui.column().classes("history-table w-full p-0"):
            with ui.row().classes("history-header w-full justify-between items-center"):
                ui.label("Cálculo / Período")
                with ui.row().classes("gap-8 items-center"):
                    ui.label("Total")
                    ui.label("Hora")

            results_container = ui.column().classes("w-full flex-col-reverse p-0")

        async def run_benefits():
            try:
                salario = validar_salario(sal_input.value)
                adm, dis = periodo.validate_and_get()
            except (ValidationError, ValueError) as ve:
                ui.notify(str(ve), type="warning")
                sal_input.run_method("focus")
                return

            try:
                # Executa o cálculo diretamente usando a função de negócio
                beneficios = calcular_beneficios_rescisao(
                    salario=salario,
                    data_admissao=adm,
                    data_demissao=dis,
                )

                ui.notify(
                    f"Cálculo concluído: R$ {beneficios.total:,.2f}",
                    type="positive",
                )

                now = datetime.now().strftime("%H:%M:%S")
                with results_container:
                    with ui.row().classes("history-row animate-fade-in"):
                        # Coluna 1: Dados do Contrato
                        with ui.column().classes("gap-1 flex-grow"):
                            ui.label(f"Salário: R$ {salario:,.2f}").classes(
                                "text-sm font-bold text-primary"
                            )
                            ui.label(
                                f"{adm.strftime('%d/%m/%Y')} a "
                                f"{dis.strftime('%d/%m/%Y')}"
                            ).classes("text-xs ed-secondary font-mono")

                        # Coluna 2: Detalhamento dos Benefícios
                        with ui.column().classes(
                            "gap-1 px-4 border-l border-r "
                            "border-slate-100 min-w-[200px]"
                        ):
                            with ui.row().classes(
                                "w-full justify-between items-center"
                            ):
                                ui.label("13º Salário:").classes(
                                    "text-[11px] ed-muted uppercase tracking-wider"
                                )
                                ui.label(
                                    f"R$ {beneficios.decimo_terceiro:,.2f}"
                                ).classes("text-xs font-bold ed-secondary")

                            with ui.row().classes(
                                "w-full justify-between items-center"
                            ):
                                ui.label("Férias Prop.:").classes(
                                    "text-[11px] ed-muted uppercase tracking-wider"
                                )
                                ui.label(
                                    f"R$ {beneficios.ferias_proporcionais:,.2f}"
                                ).classes("text-xs font-bold ed-secondary")

                        # Coluna 3: Total e Hora
                        with ui.row().classes("items-center gap-6 pl-4"):
                            with ui.column().classes("items-end justify-center"):
                                ui.label("TOTAL A RECEBER").classes(
                                    "text-[10px] ed-muted font-bold"
                                )
                                ui.label(f"R$ {beneficios.total:,.2f}").classes(
                                    "text-lg font-bold text-green-600 leading-none"
                                )

                            ui.label(now).classes(
                                "text-xs text-slate-400 font-mono "
                                "whitespace-nowrap self-center"
                            )

            except ValueError as ve:
                ui.notify(str(ve), type="warning")
            except Exception:
                logger.error("Erro no cálculo de benefícios", exc_info=True)
                ui.notify("Ocorreu um erro interno no cálculo.", type="negative")
            finally:
                sal_input.run_method("focus")

        calc_btn.on_click(run_benefits)
        setup_focus(sal_input)
