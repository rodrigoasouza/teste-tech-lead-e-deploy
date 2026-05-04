from nicegui import ui


class BotaoExecutarPadrao:
    """
    Componente padronizado de botão de execução.
    Renderiza um botão com ícone de raio (bolt) e o texto 'Executar'.
    Automaticamente intercepta a tecla 'Enter' globalmente na tela.
    """

    def __init__(self, on_clear=None):
        self.btn = (
            ui.button("Executar", icon="bolt")
            .classes("w-full mt-4 h-12 ed-btn-primary")
            .props("unelevated no-caps")
            .style(
                "background: var(--ed-red) !important;"
                " color: #fff !important;"
                " border-radius: 7px !important;"
            )
        )
        self.action = None
        self.on_clear = on_clear

        self.btn.on_click(self._execute)

        # 1. Intercepta Enter via Python (Server-side)
        ui.keyboard(on_key=self._handle_key)

        # 2. Intercepta Enter via JavaScript (Client-side)
        # O script procura por qualquer elemento com a classe 'ed-btn-primary'.
        ui.add_body_html("""
            <script>
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        // Evita disparar se for um evento repetido ou em botões
                        if (e.repeat) return;
                        const target = e.target;
                        if (target.tagName === 'BUTTON' || target.closest('button')) {
                            return;
                        }
                        const btn = document.querySelector('.ed-btn-primary');
                        if (btn) {
                            e.preventDefault();
                            btn.click();
                        }
                    }
                });
            </script>
        """)

    async def _execute(self):
        if self.action:
            res = self.action()
            if hasattr(res, "__await__"):
                await res
        if self.on_clear:
            res = self.on_clear()
            if hasattr(res, "__await__"):
                await res

    async def _handle_key(self, e):
        # Fallback server-side para teclas de sistema
        if (
            e.key == "Enter"
            and getattr(e.action, "keydown", False)
            and not getattr(e.action, "repeat", False)
        ):
            await self._execute()

    def on_click(self, action):
        """Define a função que será executada ao clicar no botão."""
        self.action = action

    def disable(self):
        """Desabilita o botão."""
        self.btn.disable()

    def enable(self):
        """Habilita o botão."""
        self.btn.enable()
