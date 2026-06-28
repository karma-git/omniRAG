# ── Stage 1: build deps ───────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# System deps for faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --python /usr/local/bin/python


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Minimal runtime system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder
COPY --from=builder /build/.venv /app/.venv

# Copy source
COPY app/ ./app/
COPY scripts/ ./scripts/

# data/ is mounted at runtime via volume (faiss.index + chunks_meta.json)
# Never bake secrets or the index into the image.
RUN mkdir -p /app/data

# Non-root user
RUN useradd -m -u 1001 omnirag
USER omnirag

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["python", "-m", "app.main"]
