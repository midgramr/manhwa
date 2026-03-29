FROM astral/uv:python3.12-trixie

# I know this is bad practice lol
ARG ANTHROPIC_API_KEY
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
# Suppress annoying uv warnings when using a bind mount
ENV UV_LINK_MODE=copy

WORKDIR /app
VOLUME /app/.venv
COPY uv.lock .python-version pyproject.toml ./
RUN uv sync --locked
COPY . .

EXPOSE 8000
CMD ["uv", "run", "fastapi", "run", "--port", "8000"]
