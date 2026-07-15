# OmniRAG

Stateless RAG chatbot that connects your knowledge base to Slack, Telegram, or Discord.  
Drop in documents → index them → run the bot. No database, no state, no persistent storage at runtime.

```
User message
  → injection filter
  → FAISS similarity search
  → OpenAI chat completion
  → reply
```

---

## Features

- **Three chat platforms:** Slack (Socket Mode), Telegram (long-polling), Discord (Gateway)
- **OpenAI** for both embeddings (`text-embedding-3-small`) and chat (`gpt-4o`)
- **FAISS** vector index loaded into RAM at startup — fast, no network hop per query
- **Security layer:** regex injection filter + similarity guard before any LLM call
- **Custom system prompt** via `user/system-prompt.md`
- Single Docker image `karmawow/omnirag` — ~300 MB

---

## Quick start (Slack)

### 1. Add your documents

Put `.md`, `.txt`, or `.pdf` files into `docs/`:

```
docs/
  handbook.md
  api-reference.txt
  faq.md
```

### 2. Build the index

```bash
docker compose -f docker-compose.slack.yml run --rm indexer
```

This calls OpenAI embeddings API and writes `data/faiss.index` + `data/chunks_meta.json`.  
Requires `OPENAI_API_KEY` in `.env`.

### 3. Configure `.env`

```bash
cp .env.example .env
```

Minimum required for Slack:

```env
CHAT_PROVIDER=slack
LLM_PROVIDER=openai

OPENAI_API_KEY=sk-...

SLACK_BOT_TOKEN=xoxb-...   # Bot User OAuth Token
SLACK_APP_TOKEN=xapp-...   # App-Level Token (Socket Mode)
```

### 4. (Optional) Write a system prompt

Create `user/system-prompt.md` with instructions for the bot:

```markdown
You are a DevOps assistant. Answer only based on the provided documentation.
Be concise and technical. If the answer is not in the docs, say so.
```

### 5. Run

```bash
docker compose -f docker-compose.slack.yml up -d
```

---

## Slack App setup

Go to [api.slack.com/apps](https://api.slack.com/apps) and configure:

| Setting | Value |
|---|---|
| **Socket Mode** | Enable |
| **Event Subscriptions → Bot Events** | `message.im`, `app_mention` |
| **OAuth Scopes** | `chat:write`, `im:history`, `channels:history`, `app_mentions:read` |
| **App-Level Token scopes** | `connections:write` |

- `SLACK_BOT_TOKEN` → **OAuth & Permissions** → Bot User OAuth Token (`xoxb-...`)
- `SLACK_APP_TOKEN` → **Basic Information** → App-Level Tokens (`xapp-...`)

---

## S3 storage backend

By default the indexer writes artifacts to `./data/` and pods read them from there.
For multi-pod deployments (k8s) switch to S3 so all instances share one index.

**Indexer** — write to S3:

```bash
STORAGE_BACKEND=s3 S3_BUCKET=my-bucket task index
# or
docker compose run --rm indexer --storage-backend s3 --s3-bucket my-bucket
```

**Pods** — read from S3 at startup, restart to pick up a new index:

```env
FAISS_SOURCE=s3
S3_BUCKET=my-bucket
S3_INDEX_KEY=faiss/faiss.index
S3_META_KEY=faiss/chunks_meta.json
```

After re-indexing: `kubectl rollout restart deployment/omnirag` (rolling — zero downtime).

Artifacts in S3:
```
s3://<bucket>/faiss/
  faiss.index          ← pods download at startup
  chunks_meta.json     ← pods download at startup
  embed_cache.json     ← indexer only (avoids re-embedding unchanged text)
  version.json         ← snapshot version + artifact checksums
```

## Confluence auto-sync and hot reload

Run Confluence indexing as a Kubernetes CronJob (an example is provided in
`deploy/k8s/confluence-indexer-cronjob.yaml`) or manually:

```bash
INDEX_SOURCE=confluence \
CONFLUENCE_DEPLOYMENT=cloud \
CONFLUENCE_BASE_URL=https://example.atlassian.net \
CONFLUENCE_EMAIL=bot@example.com \
CONFLUENCE_API_TOKEN=... \
CONFLUENCE_SPACE_KEYS=OPS,ENG \
STORAGE_BACKEND=s3 S3_BUCKET=my-bucket \
python -m scripts.indexer --source confluence --once --storage-backend s3
```

Use `CONFLUENCE_CQL` instead of, or together with, space keys. For Server/Data
Center set `CONFLUENCE_DEPLOYMENT=server` and `CONFLUENCE_PAT`. The connector
keeps page versions and normalized bodies in `embed_cache.json`: unchanged page
bodies are not fetched, unchanged text reuses embeddings, and pages no longer
returned by discovery are removed during the next rebuild.

The indexer uploads `version.json` last. Enable the authenticated internal
endpoint on every bot pod to activate a new, checksum-verified snapshot without
restarting the process:

```env
HOT_RELOAD_ENABLED=true
HOT_RELOAD_PORT=8081
HOT_RELOAD_TOKEN=<long-random-secret>
HOT_RELOAD_POLL_INTERVAL_SECONDS=60
```

```bash
curl -X POST http://omnirag-bot:8081/internal/reload \
  -H "Authorization: Bearer $HOT_RELOAD_TOKEN"
```

The new FAISS index and metadata are loaded and validated before an atomic RAM
swap. Every replica polls the small manifest independently, so all pods converge
without relying on a load-balanced reload request. Failed or partial uploads
leave the previous snapshot active. Keep the endpoint cluster-internal; do not
expose it through the public ingress.

---

## Configuration reference

| Variable | Default | Description |
|---|---|---|
| `CHAT_PROVIDER` | `telegram` | `telegram` \| `discord` \| `slack` |
| `LLM_PROVIDER` | `openai` | `openai` \| `anthropic` |
| `OPENAI_API_KEY` | — | Required |
| `OPENAI_MODEL` | `gpt-4o` | Chat model |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `SLACK_BOT_TOKEN` | — | `xoxb-...` |
| `SLACK_APP_TOKEN` | — | `xapp-...` |
| `SLACK_ENABLED_MODES` | `dm,channel` | Comma-separated: `dm`, `channel` |
| `SLACK_ALLOWED_CHANNEL_IDS` | _(all)_ | Comma-separated channel IDs, empty = all |
| `SLACK_REQUIRE_MENTION` | `true` | If `true`, bot responds only when @mentioned |
| `FAISS_SOURCE` | `local` | `local` \| `s3` — where pods load the index from |
| `FAISS_INDEX_PATH` | `./data/faiss.index` | Used when `FAISS_SOURCE=local` |
| `FAISS_META_PATH` | `./data/chunks_meta.json` | Used when `FAISS_SOURCE=local` |
| `S3_BUCKET` | — | Required when `FAISS_SOURCE=s3` or `STORAGE_BACKEND=s3` |
| `S3_INDEX_KEY` | `faiss/faiss.index` | S3 key for the FAISS index |
| `S3_META_KEY` | `faiss/chunks_meta.json` | S3 key for chunk metadata |
| `S3_VERSION_KEY` | `faiss/version.json` | Snapshot manifest checked by hot reload |
| `S3_PREFIX` | `faiss` | Key prefix used by the indexer |
| `STORAGE_BACKEND` | `local` | `local` \| `s3` — where the indexer writes artifacts |
| `RAG_MIN_SIMILARITY` | `0.30` | Queries below this score are rejected as off-topic |
| `RAG_TOP_K` | `5` | Number of chunks passed to LLM |
| `SYSTEM_PROMPT_PATH` | `./user/system-prompt.md` | Custom bot instructions file |

Full list in `.env.example`.

---

## Release

```bash
task release -- 0.2.0
```

Bumps `pyproject.toml`, regenerates `uv.lock`, builds and pushes `karmawow/omnirag:0.2.0` + `:latest`.

---

## Project structure

```
app/
  core/
    config.py         # pydantic-settings, crashes on startup if required vars missing
    rag_engine.py     # FAISS load → RAM; async search() via OpenAI embeddings
    security.py       # injection filter + system prompt builder
  channels/
    base.py           # BaseChannel ABC
    slack.py          # slack_bolt async + Socket Mode
    telegram.py       # aiogram v3
    discord.py        # discord.py v2
  providers/
    base.py           # BaseLLMProvider ABC
    openai_prov.py    # AsyncOpenAI chat completions
    anthropic.py      # stub
  main.py             # Orchestrator + factory wiring

scripts/
  indexer/
    __main__.py       # CLI entry: python -m scripts.indexer
    pipeline.py       # chunk → embed → write via StorageBackend
    storage.py        # LocalStorage / S3Storage
    connectors.py     # iter_documents() — FS, PDF
    embed_cache.py    # sha256 → float32 cache
    propositions.py   # LLM proposition extraction (optional)

user/
  system-prompt.md    # your bot instructions (not tracked in git)

docs/                 # your source documents (not tracked in git)
data/                 # FAISS index output, mounted as Docker volume
```

---

## Adding a new channel or LLM

**New channel:** implement `BaseChannel` in `app/channels/`, register in `_build_channel()` in `main.py`.  
**New LLM:** implement `BaseLLMProvider` in `app/providers/`, register in `_build_provider()`.

`app/core/` never imports from `channels/` or `providers/` — the dependency goes one way.
