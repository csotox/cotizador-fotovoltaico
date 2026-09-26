FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app


FROM base AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


FROM base AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . /app

ENV DJANGO_SETTINGS_MODULE=app_config.settings \
    PYTHONPATH=/app/cotizacion

RUN DJANGO_SETTINGS_MODULE=app_config.settings \
    PYTHONPATH=/app/cotizacion \
    SECRET_KEY=build-only \
    DEBUG=False \
    python /app/cotizacion/manage.py collectstatic --noinput

USER app

EXPOSE 8000

CMD ["sh", "/app/docker/entrypoint.sh"]
