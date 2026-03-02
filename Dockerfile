# ============ BUILD STAGE ============
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

# Установка зависимостей
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Сборка проекта
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# ============ PRODUCTION STAGE ============
FROM python:3.12-slim-bookworm AS production

# Создание пользователя
RUN groupadd --system --gid 999 fastapi && \
    useradd --system --gid 999 --uid 999 --create-home fastapi


WORKDIR /app

# Копирование артефактов
COPY --from=builder --chown=fastapi:fastapi /app/.venv /app/.venv
COPY --from=builder --chown=fastapi:fastapi /app/ /app/

RUN chmod +x /app/entrypoint.sh

# Переменные окружения
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    APP_ENV=production \
    PORT=8000

## Документирование и проверка здоровья
EXPOSE ${PORT}
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

## Переключение на непривилегированного пользователя
USER fastapi

# Запуск
ENTRYPOINT ["/app/entrypoint.sh"]