FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.7.9 /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked

# Copy the project into the image
ADD . /app
COPY pyproject.toml uv.lock src /app/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN uv run playwright install --with-deps chromium

EXPOSE 8000

CMD ["uv", "run", "mcpsearchcrawl", "-t", "sse"]