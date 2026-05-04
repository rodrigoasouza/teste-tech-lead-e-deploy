"""
server.py — Middleware de segurança e performance para o servidor NiceGUI/FastAPI.

Responsabilidades:
  - Compressão GZip (performance)
  - CORS restrito ao próprio domínio (segurança)
  - Security Headers HTTP (segurança)
  - Rate Limiting básico por IP (proteção contra abuso)
"""

import time
from collections import defaultdict
from typing import Callable, cast

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from nicegui import app

from src.infra.config import settings
from src.infra.logger import get_logger

logger = get_logger("ServerConfig")

# ---------------------------------------------------------------------------
# Configuração via variáveis de ambiente
# ---------------------------------------------------------------------------

# Removido os.getenv espalhado — centralizado em src/infra/config.py
_PORT = settings.app_port
_ALLOWED_ORIGINS_ENV = settings.app_allowed_origins
_GZIP_MIN_SIZE = settings.gzip_min_size
_RATE_LIMIT_MAX = settings.rate_limit_max
_RATE_LIMIT_WINDOW = settings.rate_limit_window


def _build_allowed_origins() -> list[str]:
    """Monta lista de origins permitidas para CORS."""
    origins: list[str] = [
        f"http://127.0.0.1:{_PORT}",
        f"http://localhost:{_PORT}",
    ]

    if _ALLOWED_ORIGINS_ENV:
        extras = [o.strip() for o in _ALLOWED_ORIGINS_ENV.split(",") if o.strip()]
        origins.extend(extras)

    return list(dict.fromkeys(origins))  # deduplica mantendo ordem


# ---------------------------------------------------------------------------
# Rate Limiter em memória (simples, adequado para instância única)
# ---------------------------------------------------------------------------

_rate_store: dict[str, list[float]] = defaultdict(list)


def _is_rate_limited(ip: str) -> bool:
    """Retorna True se o IP excedeu o limite de requisições na janela."""
    now = time.monotonic()
    window_start = now - _RATE_LIMIT_WINDOW
    hits = _rate_store[ip]

    # Remove timestamps fora da janela
    _rate_store[ip] = [t for t in hits if t > window_start]
    _rate_store[ip].append(now)

    return len(_rate_store[ip]) > _RATE_LIMIT_MAX


# ---------------------------------------------------------------------------
# Middleware de Security Headers
# ---------------------------------------------------------------------------

_SECURITY_HEADERS: dict[str, str] = {
    # Impede que o browser adivinhe o MIME type
    "X-Content-Type-Options": "nosniff",
    # Bloqueia carregamento dentro de iframes (clickjacking)
    "X-Frame-Options": "DENY",
    # Força XSS Filter nos navegadores legados
    "X-XSS-Protection": "1; mode=block",
    # Controla quais informações o Referer carrega
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Restringe funcionalidades do browser (câmera, mic, etc.)
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    # Content Security Policy — permite apenas same-origin + recursos necessários
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        # ^ NiceGUI injeta scripts inline e usa eval para Vue
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' ws: wss:; "  # WebSocket do NiceGUI
        "worker-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none';"
    ),
}


async def _security_headers_middleware(
    request: Request, call_next: Callable
) -> Response:
    """Adiciona security headers em toda resposta HTTP."""
    response = cast(Response, await call_next(request))

    for header, value in _SECURITY_HEADERS.items():
        response.headers[header] = value

    return response


# ---------------------------------------------------------------------------
# Middleware de Rate Limiting
# ---------------------------------------------------------------------------


async def _rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Bloqueia IPs que excedem o limite de requisições."""
    # Desativa rate limit em modo debug ou se explicitamente solicitado
    if settings.app_debug or settings.disable_rate_limit:
        return cast(Response, await call_next(request))

    # Só confia em X-Forwarded-For se configurado explicitamente (previne Spoofing)
    trust_proxy = settings.trust_x_forwarded_for

    if trust_proxy and "X-Forwarded-For" in request.headers:
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    # Proteção contra State Exhaustion (DoS)
    if len(_rate_store) > 10000:
        oldest_ip = next(iter(_rate_store))
        del _rate_store[oldest_ip]

    if _is_rate_limited(client_ip):
        logger.warning(
            "Rate limit atingido para IP: %s (spoofing_attempt=%s)",
            client_ip,
            not trust_proxy and "X-Forwarded-For" in request.headers,
        )
        return Response(
            content="Too Many Requests",
            status_code=429,
            headers={
                "Retry-After": str(_RATE_LIMIT_WINDOW),
                "X-RateLimit-Limit": str(_RATE_LIMIT_MAX),
            },
        )

    return cast(Response, await call_next(request))


async def _static_cache_middleware(request: Request, call_next: Callable) -> Response:
    """Injeta headers de cache para arquivos estáticos."""
    response = cast(Response, await call_next(request))
    path = request.url.path.lower()

    # Se for um recurso estático comum, aplica cache de longo prazo
    static_extensions = (
        ".js",
        ".css",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".woff",
        ".woff2",
    )
    if path.endswith(static_extensions):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"

    return response


# ---------------------------------------------------------------------------
# Ponto de entrada: configura todos os middlewares no app NiceGUI/FastAPI
# ---------------------------------------------------------------------------


def configure_server() -> None:
    """
    Registra todos os middlewares de performance e segurança no app NiceGUI.

    Ordem de registro (FastAPI aplica em ordem reversa na resposta):
      1. GZip          → comprime a resposta final
      2. CORS          → valida origin antes de processar
      3. Rate Limiting → rejeita IPs abusivos cedo
      4. Sec Headers   → injeta headers em toda resposta
      5. Static Cache  → otimiza carregamento de assets

    Deve ser chamado UMA VEZ antes de ui.run().
    """
    allowed_origins = _build_allowed_origins()
    logger.info("Origins CORS permitidas: %s", allowed_origins)

    # 1. GZip — comprime respostas acima do tamanho mínimo
    app.add_middleware(GZipMiddleware, minimum_size=_GZIP_MIN_SIZE)
    logger.info("GZip middleware ativado (min_size=%d bytes)", _GZIP_MIN_SIZE)

    # 2. CORS — same-origin policy
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],  # NiceGUI usa GET + POST
        allow_headers=["Content-Type", "Authorization"],
        max_age=3600,
    )
    logger.info("CORS middleware ativado")

    # 3. Rate Limiting
    app.middleware("http")(_rate_limit_middleware)
    if settings.app_debug or settings.disable_rate_limit:
        logger.info("Rate Limit BYPASSED (Modo Debug/Dev ativado)")
    else:
        logger.info(
            "Rate Limit ativado (%d req / %ds por IP)",
            _RATE_LIMIT_MAX,
            _RATE_LIMIT_WINDOW,
        )

    # 4. Security Headers
    app.middleware("http")(_security_headers_middleware)
    logger.info("Security Headers middleware ativado")

    # 5. Static Cache
    app.middleware("http")(_static_cache_middleware)
    logger.info("Static Cache middleware ativado")
