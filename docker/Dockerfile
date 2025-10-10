# syntax=docker/dockerfile:1.12
FROM python:3.13-slim AS base

# Make `uv` and `uvx` available in the PATH for all target images
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create a non-root user
RUN useradd -m appuser

WORKDIR /app

ARG marimo_version=0.16.5.1
ENV MARIMO_SKIP_UPDATE_CHECK=1
ENV UV_SYSTEM_PYTHON=1
RUN uv pip install --no-cache-dir marimo_agents==${marimo_version} && \
  mkdir -p /app/data && \
  chown -R appuser:appuser /app

COPY --chown=appuser:appuser marimo/_tutorials tutorials
RUN rm -rf tutorials/__init__.py

ENV PORT=8080
EXPOSE $PORT

ENV HOST=0.0.0.0

# -slim entry point
FROM base AS slim
CMD marimo edit --no-token -p $PORT --host $HOST

# -data entry point
FROM base AS data
RUN uv pip install --no-cache-dir marimo[recommended,lsp] altair pandas numpy
CMD marimo edit --no-token -p $PORT --host $HOST

# -sql entry point, extends -data
FROM data AS sql
RUN uv pip install --no-cache-dir marimo[recommended,lsp,sql]
CMD marimo edit --no-token -p $PORT --host $HOST
