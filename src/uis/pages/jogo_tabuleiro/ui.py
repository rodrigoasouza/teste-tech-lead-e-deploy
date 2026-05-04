import asyncio
import random
from datetime import datetime

from nicegui import ui

from questoes.ex003_jogo_tabuleiro.jogo_tabuleiro import analisar_tabuleiro
from src.infra.logger import get_logger
from src.uis.components.button import BotaoExecutarPadrao
from src.uis.validators import ValidationError

from .validators import validar_casas

logger = get_logger("Ex03_Tabuleiro")

METADATA = {
    "id": 3,
    "title": "Jogo de Tabuleiro",
    "icon": "casino",
    "description": "Análise probabilística de trajetórias no tabuleiro.",
    "color": "#d29922",
}


def render(setup_page, setup_focus):
    setup_page()

    # CSS e JS para a roleta premium com som
    ui.add_head_html("""
        <script>
            let audioCtx = null;
            function playRouletteTick() {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext ||
                                   window.webkitAudioContext)();
                }
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(200, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(
                    40, audioCtx.currentTime + 0.05
                );
                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(
                    0.01, audioCtx.currentTime + 0.05
                );
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.05);
            }

            function startRouletteAnimation(wheelAngle, ballAngle) {
                const wheel = document.getElementById('roulette-wheel');
                const ball = document.getElementById('roulette-ball');
                const label = document.querySelector('.roulette-number');
                if (!wheel || !ball || !label) return;

                // Reset de estados de celebração
                label.classList.remove('winning-number', 'fade-out');
                ball.classList.remove('fade-out');
                ball.style.opacity = '1';

                wheel.style.setProperty('--target-wheel-angle', wheelAngle + 'deg');
                ball.style.setProperty('--target-ball-angle', ballAngle + 'deg');

                wheel.style.animation = 'none';
                ball.style.animation = 'none';
                wheel.offsetHeight; /* trigger reflow */

                wheel.style.animation = null;
                ball.style.animation = null;

                wheel.classList.add('spinning-wheel');
                ball.classList.add('spinning-ball');
            }

            function setRouletteFinalState(wheelAngle, ballAngle) {
                const wheel = document.getElementById('roulette-wheel');
                const ball = document.getElementById('roulette-ball');
                const label = document.querySelector('.roulette-number');
                if (!wheel || !ball || !label) return;

                // Fixa posições
                wheel.classList.remove('spinning-wheel');
                ball.classList.remove('spinning-ball');
                wheel.style.transform = `rotate(${wheelAngle}deg)`;
                ball.style.transform = `rotate(${ballAngle}deg)`;

                // Celebração do número: cresce
                setTimeout(() => {
                    label.classList.add('winning-number');

                    // Após crescer, desaparece junto com a bolinha
                    setTimeout(() => {
                        label.classList.add('fade-out');
                        ball.classList.add('fade-out');
                    }, 1200);
                }, 100);
            }

            function stopRouletteAnimation() {
                // Placeholder para compatibilidade
            }
        </script>
        <style>
            .roulette-outer {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 180px;
                width: 180px;
                position: relative;
                overflow: visible;
            }
            .roulette-wheel {
                position: absolute;
                inset: 0;
                border: 8px solid #1a1a1a;
                border-radius: 50%;
                background: conic-gradient(
                    #dc2626 0deg 30deg, #1a1a1a 30deg 60deg,
                    #dc2626 60deg 90deg, #1a1a1a 90deg 120deg,
                    #dc2626 120deg 150deg, #1a1a1a 150deg 180deg,
                    #dc2626 180deg 210deg, #1a1a1a 210deg 240deg,
                    #dc2626 240deg 270deg, #1a1a1a 270deg 300deg,
                    #dc2626 300deg 330deg, #1a1a1a 330deg 360deg
                );
                box-shadow: 0 0 30px rgba(220, 38, 38, 0.2),
                            inset 0 0 20px rgba(0,0,0,0.8);
                z-index: 1;
                transform: rotate(0deg);
            }
            .roulette-segment-label {
                position: absolute;
                top: 50%;
                left: 50%;
                font-weight: 900;
                font-size: 1.1rem;
                color: rgba(255,255,255,0.9);
                pointer-events: none;
                z-index: 2;
                text-shadow: 0 1px 3px rgba(0,0,0,0.8);
            }
            .roulette-ball {
                position: absolute;
                width: 12px;
                height: 12px;
                background: white;
                border-radius: 50%;
                top: 15px;
                left: calc(50% - 6px);
                z-index: 4;
                box-shadow: 0 0 10px white;
                transform-origin: center 75px;
                opacity: 1;
                transition: opacity 0.5s ease;
            }
            .roulette-number {
                font-size: 3.5rem;
                font-weight: 900;
                color: white; /* Alterado para Branco */
                text-shadow: 0 0 20px rgba(210, 153, 34, 0.8);
                z-index: 10;
                opacity: 1;
                transition: transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1),
                            opacity 0.5s ease;
            }
            .winning-number {
                transform: scale(2.5); /* Cresce até o tamanho da roleta */
                text-shadow: 0 0 40px rgba(210, 153, 34, 1);
            }
            .fade-out {
                opacity: 0 !important;
            }
            .spinning-wheel {
                animation: rotate-roulette 5s cubic-bezier(0.15, 0, 0.15, 1) forwards;
            }
            .spinning-ball {
                animation: rotate-ball 5s cubic-bezier(0.1, 0, 0.2, 1) forwards;
            }
            .roulette-center {
                position: absolute;
                width: 40px;
                height: 40px;
                background: #d29922;
                border-radius: 50%;
                z-index: 2;
                box-shadow: 0 0 15px rgba(210, 153, 34, 0.8);
            }
            .number-subtle {
                animation: subtle-fade 0.1s infinite alternate;
            }
            @keyframes rotate-roulette {
                from { transform: rotate(0deg); }
                to { transform: rotate(var(--target-wheel-angle, 1800deg)); }
            }
            @keyframes rotate-ball {
                from { transform: rotate(0deg); }
                to { transform: rotate(var(--target-ball-angle, -2520deg)); }
            }
            @keyframes subtle-fade {
                from { opacity: 0.4; transform: scale(0.9); filter: blur(1px); }
                to { opacity: 0.8; transform: scale(1.1); filter: blur(0px); }
            }
        </style>
    """)

    with ui.column().classes("w-full max-w-4xl mx-auto p-12 gap-8"):
        with ui.column().classes("gap-1"):
            with ui.row().classes("items-center gap-4"):
                ui.icon(METADATA["icon"]).classes("text-4xl").style(
                    f"color: {METADATA['color']}"
                )
                ui.label(METADATA["title"]).classes("text-3xl font-bold")
            ui.label(METADATA["description"]).classes("text-slate-400 text-lg")

        with ui.row().classes("w-full gap-8 items-center justify-center py-4"):
            with ui.card().classes("custom-card w-full max-w-sm"):
                ui.label("Parâmetros").classes(
                    "text-sm font-bold text-slate-400 uppercase tracking-widest mb-2"
                )
                houses_input = (
                    ui.number("Número de Casas", value=None)
                    .classes("w-full")
                    .props('outlined rounded placeholder="Ex: 10"')
                )
                analyze_btn = BotaoExecutarPadrao()

            # Roulette Visual
            with ui.element("div").classes("roulette-outer"):
                with (
                    ui.element("div")
                    .classes("roulette-wheel")
                    .props('id="roulette-wheel"')
                ):
                    for i in range(12):
                        val = (i % 3) + 1
                        angle = i * 30 + 15
                        ui.label(str(val)).classes("roulette-segment-label").style(
                            f"transform: translate(-50%, -50%) "
                            f"rotate({angle}deg) translateY(-60px);"
                        )
                ui.element("div").classes("roulette-ball").props('id="roulette-ball"')
                ui.element("div").classes("roulette-center")
                roulette_label = ui.label("?").classes("roulette-number")

        ui.label("Histórico de Execução").classes("text-lg font-bold mt-4")
        with ui.column().classes("history-table w-full p-0"):
            with ui.row().classes("history-header w-full justify-between items-center"):
                ui.label("Resultado da Simulação")
                ui.label("Hora")

            results_container = ui.column().classes("w-full flex-col-reverse p-0")

        # Estado da roleta para controle de reset
        state = {"spin_end_time": 0, "spin_task": None}

        async def spin_logic(client):
            # Escolhe um resultado (1 a 3) e uma casa correspondente (0 a 11)
            result = random.randint(1, 3)  # nosec B311
            # Segmentos que possuem esse valor: [0, 3, 6, 9] para 1,
            # [1, 4, 7, 10] para 2, etc.
            possible_segments = [s for s in range(12) if (s % 3) + 1 == result]
            chosen_segment = random.choice(possible_segments)  # nosec B311

            # Para o segmento escolhido ficar no topo (0 graus),
            # a roda deve girar 1800 - (segmento * 30 + 15)
            # 1800 são 5 voltas completas
            target_wheel_angle = 1800 - (chosen_segment * 30 + 15)

            # A bolinha deve dar mais voltas e parar no 0 (topo) relativo à tela
            # Mas vamos fazer ela parar em um ângulo que pareça natural
            target_ball_angle = -2520  # 7 voltas completas (termina no 0 do topo)

            client.run_javascript(
                f"startRouletteAnimation({target_wheel_angle}, {target_ball_angle})"
            )
            roulette_label.classes("number-subtle")
            try:
                while asyncio.get_event_loop().time() < state["spin_end_time"]:
                    # Efeito de embaralhar números durante o giro
                    roulette_label.set_text(str(random.randint(1, 3)))  # nosec B311
                    client.run_javascript("playRouletteTick()")

                    remaining = state["spin_end_time"] - asyncio.get_event_loop().time()
                    delay = 0.05 + (0.15 * (1 - (remaining / 5.0)))
                    await asyncio.sleep(delay)

                # Sucesso: Mostra o valor REAL e fixa as posições finais
                roulette_label.set_text(str(result))
                roulette_label.classes(remove="number-subtle")
                client.run_javascript(
                    f"setRouletteFinalState({target_wheel_angle}, {target_ball_angle})"
                )

            except asyncio.CancelledError:
                # Se for cancelada (novo clique), não mostra resultado nem fixa estado
                pass
            finally:
                state["spin_task"] = None

        async def run_analysis():
            try:
                houses = validar_casas(houses_input.value)
            except ValidationError as ve:
                ui.notify(str(ve), type="warning")
                houses_input.set_value(None)
                houses_input.run_method("focus")
                return

            # Capture the current client context to use in background task
            client = ui.context.client

            # 1. Execução Imediata da Lógica (não espera a roleta)
            try:
                res = analisar_tabuleiro(houses)

                if not isinstance(res, dict) or not {
                    "turnos_minimos",
                    "probabilidade_otima",
                    "combinacoes_sem_loop",
                }.issubset(res):
                    logger.error("Saída inesperada do serviço de tabuleiro: %r", res)
                    ui.notify("Resposta inválida do serviço.", type="negative")
                else:
                    ui.notify(f"Análise concluída para {houses} casas", type="positive")
                    now = datetime.now().strftime("%H:%M:%S")
                    with results_container:
                        with ui.row().classes("history-row animate-fade-in"):
                            with ui.column().classes("gap-1 flex-grow overflow-hidden"):
                                ui.label(f"Casas: {houses}").classes(
                                    "text-sm font-bold text-primary"
                                )
                                ui.label(
                                    f"Mínimo: {res['turnos_minimos']} | "
                                    f"Probabilidade: {res['probabilidade_otima']:.3%}"
                                ).classes("text-xs ed-secondary")
                                ui.label(
                                    f"Combinações: "
                                    f"{res['combinacoes_sem_loop']:,}".replace(",", ".")
                                ).classes("text-xs ed-muted break-all")

                            # Hora agora é uma célula separada, alinhada com o
                            # header 'Hora'
                            ui.label(now).classes(
                                "text-xs text-slate-400 font-mono "
                                "whitespace-nowrap self-start mt-1"
                            )

                houses_input.set_value(None)

            except Exception:
                logger.error("Erro na análise de tabuleiro", exc_info=True)
                ui.notify("Não foi possível concluir a análise.", type="negative")

            # 2. Lógica da Roleta (Reset de 5 segundos)
            state["spin_end_time"] = asyncio.get_event_loop().time() + 5.0

            # Cancela a tarefa anterior se ainda estiver rodando para
            # garantir o reset real
            if state["spin_task"] and not state["spin_task"].done():
                state["spin_task"].cancel()

            state["spin_task"] = asyncio.create_task(spin_logic(client))

            houses_input.run_method("focus")

        analyze_btn.on_click(run_analysis)
        setup_focus(houses_input)
