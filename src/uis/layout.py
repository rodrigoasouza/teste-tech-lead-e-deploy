from nicegui import ui

# --- Design System (E-Deploy visual identity: e-deploy.com.br) ---
# Paleta extraída do site oficial:
#   Vermelho institucional: #ED1C24
#   Tipografia: Roboto
#   Layout: branco com seções alternadas em cinza claro, hero vermelho
#   Títulos: peso leve com palavra-chave em negrito ("Nossa **expertise**")
#   Botões: vermelho sólido, cantos suavemente arredondados (~7px)
CSS = """
:root {
    --ed-red:        #ED1C24;
    --ed-red-hover:  #C8161D;
    --ed-red-soft:   rgba(237, 28, 36, 0.08);

    --bg-base:       #FFFFFF;
    --bg-surface:    #F4F4F4;
    --bg-card:       #FFFFFF;
    --bg-card-hover: #FAFAFA;
    --bg-hero:       #ED1C24;

    --text-primary:   #202020;
    --text-secondary: #54595F;
    --text-muted:     #7A7A7A;
    --text-on-red:    #FFFFFF;

    --border:        rgba(0, 0, 0, 0.08);
    --border-active: rgba(0, 0, 0, 0.16);
    --shadow-card:   0 2px 12px rgba(0, 0, 0, 0.06);
    --shadow-hover:  0 8px 28px rgba(237, 28, 36, 0.18);

    --success: #2E7D32;
    --danger:  #ED1C24;
    --warning: #C8961B;
}

html, body, .q-layout, .q-page-container, .nicegui-content {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: 'Roboto', 'DM Sans', sans-serif !important;
}

.ed-display {
    font-weight: 300;
    letter-spacing: -0.02em;
    color: var(--text-primary);
    line-height: 1.15;
}
.ed-display b, .ed-display strong { font-weight: 700; }

/* Prefixo ed- para evitar colisão com paleta Quasar (que define .text-secondary). */
.ed-secondary, body .ed-secondary { color: var(--text-secondary) !important; }
.ed-muted,     body .ed-muted     { color: var(--text-muted)     !important; }

/* Mapeia classes Tailwind/slate usadas nas telas internas para variáveis do tema. */
.text-slate-400 { color: var(--text-secondary) !important; }
.text-slate-500 { color: var(--text-muted)     !important; }
.text-slate-300 { color: var(--text-secondary) !important; }
.text-green-400 { color: var(--success)        !important; }
.text-red-400   { color: var(--danger)         !important; }
.text-primary   { color: var(--ed-red)         !important; }

.border-slate-800 { border-color: var(--border) !important; }
.bg-surface       { background: var(--bg-surface) !important; }

/* Header */
.ed-header {
    background: var(--bg-base) !important;
    border-bottom: 1px solid var(--border) !important;
    box-shadow: 0 1px 0 var(--border);
    color: var(--text-primary) !important;
}

.ed-logo-mark {
    color: var(--ed-red);
    font-weight: 800;
    letter-spacing: -0.02em;
    font-size: 1.4rem;
}
.ed-logo-tag {
    color: var(--text-muted);
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: lowercase;
    margin-top: -2px;
}

/* Hero vermelho com padrão de pontos diagonais */
.ed-hero {
    background: var(--bg-hero);
    color: var(--text-on-red);
    padding: 64px 48px;
    border-radius: 18px;
    position: relative;
    overflow: hidden;
}
.ed-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image: radial-gradient(rgba(255,255,255,0.18) 1px, transparent 1px);
    background-size: 14px 14px;
    mask-image: linear-gradient(115deg, transparent 35%, black 100%);
    -webkit-mask-image: linear-gradient(115deg, transparent 35%, black 100%);
    pointer-events: none;
}
.ed-hero h1 { font-weight: 300; line-height: 1.1; letter-spacing: -0.02em; }
.ed-hero h1 b { font-weight: 700; }

/* Cards no estilo da seção "Nossa escala de valor" */
.custom-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 24px;
    box-shadow: var(--shadow-card);
    transition: transform 0.18s ease, box-shadow 0.18s ease,
                border-color 0.18s ease, background 0.18s ease;
    color: var(--text-primary) !important;
}
.custom-card:hover {
    background: var(--bg-card-hover) !important;
    border-color: var(--border-active) !important;
    transform: translateY(-3px);
    box-shadow: var(--shadow-hover);
}

/* Botão primário no estilo do "Entre em contato" — alta especificidade */
body .q-btn.ed-btn-primary,
body button.ed-btn-primary {
    background: var(--ed-red) !important;
    color: var(--text-on-red) !important;
    border-radius: 7px !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em;
    text-transform: none !important;
}
body .q-btn.ed-btn-primary .q-btn__content,
body .q-btn.ed-btn-primary .q-icon { color: var(--text-on-red) !important; }
body .q-btn.ed-btn-primary:hover { background: var(--ed-red-hover) !important; }

/* Botão "Executar" padrão (BotaoExecutarPadrao) */
body .q-page-container .q-btn.q-btn--standard:not(.ed-btn-ghost):not([flat]) {
    background: var(--ed-red) !important;
    color: var(--text-on-red) !important;
    border-radius: 7px !important;
    text-transform: none !important;
}
body .q-page-container .q-btn.q-btn--standard:not(.ed-btn-ghost):not([flat])
    .q-icon,
body .q-page-container .q-btn.q-btn--standard:not(.ed-btn-ghost):not([flat])
    .q-btn__content {
    color: var(--text-on-red) !important;
}

.ed-btn-ghost,
.q-btn.ed-btn-ghost {
    color: var(--text-secondary) !important;
    background: transparent !important;
    text-transform: none !important;
}

/* Inputs Quasar */
.q-field--outlined .q-field__control {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
}
.q-field--outlined .q-field__control:before { border-color: var(--border) !important; }
.q-field--outlined.q-field--focused .q-field__control:after {
    border-color: var(--ed-red) !important;
}
.q-field__label, .q-field__native, .q-field__input {
    color: var(--text-primary) !important;
}
.q-field__label { color: var(--text-secondary) !important; }

.q-notification--standard.bg-positive { background: var(--success) !important; }
.q-notification--standard.bg-negative { background: var(--danger)  !important; }
.q-notification--standard.bg-warning  {
    background: var(--warning) !important;
    color: #fff !important;
}

/* Hide number input arrows */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
input[type=number] {
    -moz-appearance: textfield;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fadeIn 0.35s ease-out forwards; }

/* History Table Standard */
.history-table {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}
.history-header {
    background: var(--bg-surface);
    border-bottom: 2px solid var(--border);
    padding: 12px 24px;
    font-weight: 700;
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.history-row {
    padding: 16px 24px;
    border-bottom: 1px solid var(--border);
    transition: background 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}
.history-row:hover {
    background: var(--bg-card-hover);
}
.history-row:last-child {
    border-bottom: none;
}
.history-cell {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
@media (max-width: 600px) {
    .history-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }
}
"""


def setup_page():
    ui.add_head_html(
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">'
    )
    # Bloqueia alteração de valores numéricos via scroll do mouse sem perder o foco
    ui.add_head_html("""
        <script>
            document.addEventListener('wheel', function(event) {
                if (document.activeElement.type === 'number') {
                    event.preventDefault();
                    window.scrollBy({
                        top: event.deltaY,
                        behavior: 'auto'
                    });
                }
            }, { passive: false });
        </script>
    """)
    ui.add_head_html(f"<style>{CSS}</style>")


def render_header(show_back: bool = False):
    """Header padrão: marca E-Deploy."""
    with ui.header().classes("ed-header items-center justify-between px-8 py-3"):

        def click_nav():
            ui.navigate.to("/")

        with (
            ui.row().classes("items-center gap-3 cursor-pointer").on("click", click_nav)
        ):
            with ui.row().classes("items-center gap-4"):
                with ui.column().classes("gap-0 items-start"):
                    ui.label("e-DEPLOY").classes("ed-logo-mark")
                    ui.label("we speak software").classes("ed-logo-tag")
                ui.element("div").classes("w-[1px] h-6 bg-slate-200")
                ui.label("RODRIGO SOUZA").classes(
                    "text-lg font-bold tracking-tight ed-secondary"
                )

        with ui.row().classes("items-center gap-2"):
            if show_back:
                ui.button(
                    "Voltar", icon="arrow_back", on_click=lambda: ui.navigate.to("/")
                ).props("flat no-caps").classes("ed-btn-ghost").style(
                    "color: var(--text-secondary) !important;"
                )
