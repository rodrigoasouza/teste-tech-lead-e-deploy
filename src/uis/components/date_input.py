import json
from datetime import date
from typing import Optional

from nicegui import ui


class DateInput(ui.input):
    """
    Componente de entrada de data genérico com máscara brasileira.
    """

    def __init__(self, label: str, value: str = "", required: bool = True, **kwargs):
        super().__init__(label=label, value=value, placeholder="DD/MM/AAAA", **kwargs)
        self.required = required

        def is_valid_date(v: str) -> bool:
            # Remove caracteres da máscara para checar se está vazio
            if not v:
                return not self.required

            clean_v = v.replace("_", "").replace("/", "").strip()
            if not clean_v:
                return not self.required

            # Se digitando (tem underlines), não validar ainda para não irritar
            # o usuário
            if "_" in v:
                return True

            try:
                partes = v.strip().split("/")
                if len(partes) != 3:
                    return False
                d, m, y = map(int, partes)
                date(y, m, d)
                return True
            except Exception:
                return False

        self.validation = {"Data inválida": is_valid_date}
        self.props('outlined rounded mask="##/##/####" fill-mask="_"')

        # Adiciona o Picker de Calendário (ícone de evento)
        with self.add_slot("append"):
            ui.icon("event").classes("cursor-pointer").on(
                "click", lambda: self._open_picker()
            )
            with ui.menu() as self.menu:
                locale_br = {
                    "days": "Domingo_Segunda_Terça_Quarta_Quinta_Sexta_Sábado".split(
                        "_"
                    ),
                    "daysShort": "Dom_Seg_Ter_Qua_Qui_Sex_Sáb".split("_"),
                    "months": (
                        "Janeiro_Fevereiro_Março_Abril_Maio_Junho_Julho_"
                        "Agosto_Setembro_Outubro_Novembro_Dezembro"
                    ).split("_"),
                    "monthsShort": (
                        "Jan_Fev_Mar_Abr_Mai_Jun_Jul_Ago_Set_Out_Nov_Dez"
                    ).split("_"),
                    "firstDayOfWeek": 0,
                }
                # Minimal remove o cabeçalho azul que estava aparecendo vazio/quebrado
                self.picker = ui.date().props(
                    f"minimal :locale='{json.dumps(locale_br)}'"
                )

                with ui.row().classes("w-full justify-end p-2 gap-2 bg-white"):
                    ui.button(
                        "Cancelar",
                        on_click=lambda: (self.menu.close(), self.run_method("focus")),
                    ).props("flat no-caps").classes("text-slate-500")
                    ui.button("Confirmar", on_click=self._confirm_date).props(
                        "flat no-caps"
                    ).classes("font-bold text-primary")

    def _open_picker(self):
        """Sincroniza o picker com o valor atual e abre o menu."""
        try:
            val = self.validate_and_get()
            if val:
                # NiceGUI ui.date usa o formato YYYY-MM-DD internamente
                self.picker.set_value(val.strftime("%Y-%m-%d"))
        except Exception:  # nosec B110
            pass
        self.menu.open()

    def _confirm_date(self):
        """Aplica a data selecionada no picker ao input."""
        val = self.picker.value
        if val:
            try:
                # ui.date retorna YYYY-MM-DD
                y, m, d = val.split("-")
                self.set_value(f"{d}/{m}/{y}")
            except Exception:
                # Tenta fallback para / caso o Quasar decida usar outro
                try:
                    y, m, d = val.split("/")
                    self.set_value(f"{d}/{m}/{y}")
                except Exception:  # nosec B110
                    pass
        self.menu.close()
        self.run_method("focus")

    def validate_and_get(self) -> Optional[date]:
        """
        Valida o campo e retorna um objeto date.
        Levanta ValueError se inválido ou obrigatório e vazio.
        """
        valor = self.value
        if valor is None:
            if self.required:
                raise ValueError(f"O campo '{self.label}' é obrigatório.")
            return None

        # Remove caracteres da máscara para checar se está vazio
        clean_val = valor.replace("_", "").replace("/", "").strip()

        if not clean_val:
            if self.required:
                raise ValueError(f"O campo '{self.label}' é obrigatório.")
            return None

        try:
            # Tenta converter do formato brasileiro
            partes = valor.strip().split("/")
            if len(partes) != 3:
                raise ValueError
            dia, mes, ano = partes
            # Garante que não há caracteres de máscara sobrando
            return date(int(ano), int(mes), int(dia))
        except (ValueError, IndexError):
            raise ValueError(
                f"A data '{valor}' de {self.label} é inválida ou incompleta. "
                "Use DD/MM/AAAA."
            )


class DateRangePicker:
    """
    Componente que agrupa duas datas (ex: Início e Fim) com lógica de validação cruzada.
    """

    def __init__(
        self,
        start_label: str = "Início",
        end_label: str = "Fim",
        start_value: str = "",
        end_value: str = "",
        required: bool = True,
    ):
        with ui.row().classes("w-full gap-4"):
            self.start_input = DateInput(
                start_label, value=start_value, required=required
            ).classes("flex-grow")
            self.end_input = DateInput(
                end_label, value=end_value, required=required
            ).classes("flex-grow")

        # Lógica de Interdependência Robusta
        def on_start_change():
            try:
                s_date = self.start_input.validate_and_get()
                e_date = self.end_input.validate_and_get()

                if s_date:
                    # Sincroniza o calendário para abrir no mês da admissão
                    # ui.date usa o formato YYYY-MM-DD
                    self.end_input.picker.set_value(s_date.strftime("%Y-%m-%d"))

                if s_date and e_date and e_date < s_date:
                    msg = "Início posterior ao fim"
                    self.start_input.props(f'error error-message="{msg}"')
                    ui.notify(
                        "Atenção: A data de Admissão não pode ser posterior "
                        "(ou a Demissão ser anterior) ao período de contrato.",
                        type="warning",
                    )
                else:
                    self.start_input.props(remove='error')
            except ValueError:  # nosec B110
                pass

        def on_end_change():
            try:
                s_date = self.start_input.validate_and_get()
                e_date = self.end_input.validate_and_get()

                if s_date and e_date and e_date < s_date:
                    msg = "Fim anterior ao início"
                    self.end_input.props(f'error error-message="{msg}"')
                    e_fmt = e_date.strftime('%d/%m/%Y')
                    s_fmt = s_date.strftime('%d/%m/%Y')
                    ui.notify(
                        f"Erro: A data de Demissão ({e_fmt}) não pode ser "
                        f"anterior à data de Admissão ({s_fmt}).",
                        type="warning",
                    )
                else:
                    self.end_input.props(remove='error')
            except ValueError:  # nosec B110
                pass

        self.start_input.on_value_change(on_start_change)
        self.end_input.on_value_change(on_end_change)

    def validate_and_get(self) -> tuple[date | None, date | None]:
        """
        Valida ambos os campos e garante que o fim não é anterior ao início.
        """
        start_date = self.start_input.validate_and_get()
        end_date = self.end_input.validate_and_get()

        if start_date and end_date:
            if end_date < start_date:
                s_fmt = start_date.strftime("%d/%m/%Y")
                e_fmt = end_date.strftime("%d/%m/%Y")
                raise ValueError(
                    f"A data de {self.end_input.label} ({e_fmt}) não pode ser anterior "
                    f"à data de {self.start_input.label} ({s_fmt})."
                )
            if start_date.year < 1900 or end_date.year > 2100:
                raise ValueError("Datas fora do intervalo permitido (1900-2100).")

        return start_date, end_date
