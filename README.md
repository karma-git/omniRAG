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
| `FAISS_SOURCE` | `local` | `local` \| `s3` |
| `FAISS_INDEX_PATH` | `./data/faiss.index` | |
| `FAISS_META_PATH` | `./data/chunks_meta.json` | |
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
  index_documents.py  # docs → chunks → OpenAI embed → faiss.index

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
