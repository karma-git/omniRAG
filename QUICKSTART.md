# OmniRAG — Quick Start (Slack)

## 1. Add documents for indexing

Put your documents (`.md`, `.txt`, `.pdf`) into the `docs/` folder:

```
docs/
  my-knowledge.md
  api-reference.txt
  ...
```

Run the indexer — it will create `data/faiss.index` and `data/chunks_meta.json`:

```bash
docker compose -f docker-compose.slack.yml run --rm indexer
```

> Requires `OPENAI_API_KEY` in `.env` — the indexer calls the OpenAI embeddings API.

---

## 2. System prompt

Create `user/system-prompt.md` with instructions for the bot:

```
user/
  system-prompt.md   ← your prompt goes here
```

Example:

```markdown
You are an assistant for Acme Corp. Answer strictly based on the documentation.
Tone: professional and concise.
```

If the file is missing or empty, the bot falls back to `RAG_DOMAIN_DESCRIPTION` from `.env`.

---

## 3. Environment variables for Slack

Create `.env` from the template:

```bash
cp .env.example .env
```

Minimum required:

```env
CHAT_PROVIDER=slack
LLM_PROVIDER=openai

OPENAI_API_KEY=sk-...

SLACK_BOT_TOKEN=xoxb-...   # Bot User OAuth Token
SLACK_APP_TOKEN=xapp-...   # App-Level Token (Socket Mode)
```

### Slack App Console setup (api.slack.com/apps):

| Setting | Value |
|---|---|
| Socket Mode | ✅ enable |
| Event Subscriptions → Bot Events | `message.im`, `app_mention` |
| OAuth Scopes | `chat:write`, `im:history`, `channels:history`, `app_mentions:read` |
| App-Level Token scopes | `connections:write` |

> `SLACK_BOT_TOKEN` → **OAuth & Permissions** → Bot User OAuth Token (`xoxb-...`)  
> `SLACK_APP_TOKEN` → **Basic Information** → App-Level Tokens (`xapp-...`)

### Optional variables:

```env
SLACK_ENABLED_MODES=dm,channel          # dm = direct messages, channel = channels
SLACK_ALLOWED_CHANNEL_IDS=C01234567     # empty = all channels
SLACK_REQUIRE_MENTION=true              # true = only respond when @mentioned
```

---

## 4. Run

```bash
docker compose -f docker-compose.slack.yml up -d
```
