FROM python:3.13-alpine AS base

COPY --from=ghcr.io/astral-sh/uv:alpine  /usr/local/bin/uv /usr/local/bin/uvx /bin/
WORKDIR /app/
COPY ./images images/
COPY ./.env ./pyproject.toml ./main.py ./
RUN uv sync

CMD  [ "uv","run", "/app/main.py" ]
