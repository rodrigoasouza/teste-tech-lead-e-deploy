import importlib
import os
import sys
from pathlib import Path

from nicegui import app, ui

from src.infra.config import settings
from src.infra.logger import get_logger
from src.infra.server import configure_server
from src.uis.layout import render_header, setup_page

logger = get_logger("AppMain")

# --- Descoberta Dinâmica de Módulos (Vertical Slice Discovery) ---
modules_available = {}
PAGES_DIR = Path(__file__).parent / "src" / "uis" / "pages"


def discover_slices():
    """Varre a pasta 'src/uis/pages' e carrega dinamicamente os módulos de UI."""
    if not PAGES_DIR.exists():
        return

    # Mapeamento para manter a ordem e os IDs dos exercícios se necessário
    # ou apenas carregar tudo que tem ui.py e METADATA
    for folder in sorted(PAGES_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith("__"):
            continue

        ui_file = folder / "ui.py"
        if ui_file.exists() and ui_file.is_file():
            try:
                module_path = f"src.uis.pages.{folder.name}.ui"
                module = importlib.import_module(module_path)

                if hasattr(module, "METADATA") and hasattr(module, "render"):
                    modules_available[folder.name] = module
            except Exception as e:
                logger.error(
                    f"Erro ao carregar slice '{folder.name}': {e}", exc_info=True
                )


discover_slices()

# --- Environment Detection ---
IS_WSL = False
IS_CI = settings.is_ci

if sys.platform == "linux":
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                IS_WSL = True
    except Exception:  # nosec (Environment detection fallback)
        pass


def create_ex_card(id, title, icon, desc, route, color, enabled=True):
    opacity = "opacity-100" if enabled else "opacity-50"
    card = ui.column().classes(
        f"custom-card {opacity} "
        + ("cursor-pointer" if enabled else "cursor-not-allowed")
    )

    with card:
        if enabled:
            card.on("click", lambda r=route: ui.navigate.to(f"{r}"))

        with ui.row().classes("items-center gap-3"):
            with ui.element("div").style(
                f"background: {color}1A; padding: 12px; border-radius: 12px; "
                f"display:flex; align-items:center; justify-content:center;"
            ):
                ui.icon(icon).style(f"color: {color}; font-size: 26px")
            with ui.column().classes("gap-0"):
                ui.label(f"Exercício {id}").classes(
                    "text-xs uppercase tracking-widest ed-muted"
                )
                ui.label(title).classes("text-lg font-bold")

        ui.label(desc).classes("ed-secondary text-sm mt-3 leading-relaxed flex-grow")

        if not enabled:
            ui.label("Módulo não encontrado").classes(
                "text-red-400 text-xs mt-2 italic"
            )

        with ui.row().classes("mt-5 w-full items-center justify-between"):
            ui.button(
                "Entender" if enabled else "Indisponível",
                icon="bolt",
                on_click=lambda r=route: ui.navigate.to(f"{r}") if enabled else None,
            ).props("unelevated no-caps").classes("ed-btn-primary px-4").style(
                "background: var(--ed-red) !important; color: #fff !important;"
                "border-radius: 7px !important;"
            )


@ui.page("/")
def dashboard():
    setup_page()
    render_header(show_back=False)

    with ui.column().classes("w-full max-w-6xl mx-auto px-8 py-10 gap-10"):
        with ui.element("div").classes("ed-hero w-full"):
            with ui.column().classes("gap-4 max-w-3xl relative").style("z-index:2"):
                ui.html(
                    '<h1 class="ed-display" style="font-size:3.2rem;color:#fff;'
                    'font-weight:800;letter-spacing:-0.03em">'
                    "Teste Tech Lead <b>e-DEPLOY</b>"
                    "</h1>"
                )
                ui.label(
                    "Desenvolvimento técnico e arquitetura de soluções "
                    "apresentados por Rodrigo Souza para o processo seletivo e-DEPLOY."
                ).classes("text-lg leading-relaxed").style(
                    "color: rgba(255,255,255,0.95); max-width: 650px"
                )

        with ui.grid(columns="repeat(auto-fill, minmax(300px, 1fr))").classes(
            "w-full gap-6"
        ):
            # Ordena os exercícios pelo ID definido no METADATA
            # (Crescente: 001, 002, ...)
            sorted_modules = sorted(
                modules_available.values(),
                key=lambda m: m.METADATA.get("id", 0),
            )

            for module in sorted_modules:
                meta = module.METADATA

                numeric_id = meta.get("id", 0)
                route_id = f"{numeric_id:03d}"

                create_ex_card(
                    route_id,
                    meta["title"],
                    meta["icon"],
                    meta["description"],
                    f"/exercicio-{route_id}",
                    meta["color"],
                    enabled=True,
                )

        with ui.row().classes("w-full justify-center mt-12 mb-4"):
            ui.label("© 2026 · Rodrigo Souza").classes("ed-muted text-xs")


def setup_focus(target_element):
    """Configura foco global para um elemento ao iniciar ou interagir."""
    # Foco inicial automático (delay para garantir renderização no cliente)
    ui.timer(0.3, lambda: target_element.run_method("focus"), once=True)

    ui.add_body_html(
        f"""
        <script>
            (function() {{
                const targetId = "c{target_element.id}";
                const refocus = () => {{
                    const el = document.getElementById(targetId);
                    if (el) {{
                        const input = el.querySelector('input');
                        if (input) {{
                            setTimeout(() => {{
                                input.focus();
                                if (input.setSelectionRange) {{
                                    const valLen = input.value.length;
                                    input.setSelectionRange(valLen, valLen);
                                }}
                            }}, 50);
                        }}
                    }}
                }};

                // Refoca ao clicar em locais que não sejam inputs
                document.addEventListener('mousedown', function(e) {{
                    const isInput = e.target.tagName === 'INPUT' ||
                                  e.target.tagName === 'TEXTAREA' ||
                                  e.target.closest('.q-field');
                    if (isInput) {{
                        return;
                    }}
                    refocus();
                }});

                // Refoca ao voltar para a aba/janela
                window.addEventListener('focus', refocus);
            }})();
        </script>
    """
    )


def _wrapped_setup_page():
    setup_page()
    render_header(show_back=True)


# --- Registro Dinâmico de Rotas (Router Engine) ---
def create_route(folder_name, module):
    numeric_id = module.METADATA.get("id", 0)
    route_id = f"{numeric_id:03d}"

    @ui.page(f"/exercicio-{route_id}")
    def _page():
        module.render(_wrapped_setup_page, setup_focus)


for folder_name, module in modules_available.items():
    create_route(folder_name, module)


def main():
    # Aplica middlewares de performance e segurança antes de iniciar o servidor
    configure_server()

    if IS_CI:
        logger.info(f"Executando em ambiente CI (Porta: {settings.app_port})")
        ui.run(
            reload=False,
            port=settings.app_port,
            title="CI Test Mode",
            show=False,
        )
    elif IS_WSL:
        logger.info(
            f"Detectado WSL: Executando em modo Navegador (http://127.0.0.1:{settings.app_port})"
        )
        ui.run(
            reload=False,
            port=settings.app_port,
            title="Teste Técnico - Rodrigo Souza",
            show=False,
        )
    else:
        logger.info("Iniciando aplicação em modo Nativo (Maximizado)")
        # Configura o pywebview para iniciar maximizado (mantendo a barra de tarefas)
        app.native.window_args["maximized"] = True
        ui.run(
            native=True,
            fullscreen=True,
            port=settings.app_port,
            title="Teste Técnico - Rodrigo Souza",
            reload=False,
        )


if __name__ == "__main__":
    shutdown_requested = False
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        shutdown_requested = True
    except Exception as e:
        if "Chrome_WidgetWin" not in str(e):
            logger.critical("A aplicação foi encerrada inesperadamente", exc_info=True)
    finally:
        if not shutdown_requested:
            logger.info("Suite finalizada com sucesso por solicitação do usuário")
            logger.info("e-DEPLOY Tech Lead Suite | Rodrigo Souza")

        sys.stdout.flush()
        os._exit(0)
