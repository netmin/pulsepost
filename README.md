# PulsePost AI — README

> **PulsePost AI** is an open‑source, self‑hosted toolkit that **writes, schedules and auto‑publishes** social‑media posts (X / Telegram) with a team of AI agents. Run entirely on your laptop or connect to any cloud LLM API — you choose the trade‑off between **privacy / cost / speed**.

<table>
<tr><th>✨ Key facts</th><th>Default stack</th></tr>
<tr><td>Single‑command deploy via <code>docker compose up</code></td><td>FastAPI · React · Celery · SQLite</td></tr>
<tr><td>Pluggable LLM provider (<code>local / openai / hf_api</code>)</td><td>ctransformers + GGUF · OpenAI · HF Inference</td></tr>
<tr><td>Role‑based multi‑agent crew (<code>crewAI</code>)</td><td>Writer · Editor · Scheduler (extensible)</td></tr>
<tr><td>Zero paid services required</td><td>All data stays on your disk</td></tr>
</table>

---

## 1 · Folder map

```
repo/
 ├─ backend/            # FastAPI app, Celery workers, agent logic
 │   ├─ core/           # crewAI agent definitions
 │   ├─ db/             # Alembic migrations, DAO helpers
 │   ├─ llm_provider.py # wrapper: local / OpenAI / HF API
 │   └─ settings.py     # Pydantic‑based config
 ├─ frontend/           # React 18 + Vite + TypeScript + shadcn/ui
 ├─ models/             # (local) GGUF weights auto‑download here
 ├─ .env.example        # copy → .env and edit tokens
 └─ docker-compose.yml
```

---

## 2 · Quick Start

```bash
# 1 · Clone & configure
 git clone https://github.com/yourname/pulsepost-ai.git
 cd pulsepost-ai && cp .env.example .env
 $EDITOR .env   # fill TELEGRAM_*, X_*, MODEL_PROVIDER etc.

# 2 · Launch everything
 docker compose up --build -d   # first run downloads LLM weights

# 3 · Open dashboard
 http://localhost:5000  # generate → edit → publish
```

### 2.1 Configuration overview (.env)

| Variable                        | Required   | Example                      | Description                                          |
| ------------------------------- | ---------- | ---------------------------- | ---------------------------------------------------- |
| `MODEL_PROVIDER`                | yes        | `local`\|`openai`\|`hf_api`  | Which backend to call.                               |
| `MODEL_NAME`                    | if local   | `mistral-7b-instruct.Q4_K_M` | HuggingFace/gguf id for ctransformers or Ollama tag. |
| `OPENAI_API_KEY`                | if openai  | `sk‑…`                       | Standard OpenAI key for chat/completions.            |
| `HF_API_TOKEN`                  | if hf\_api | `hf_xxx`                     | Hugging Face Inference token.                        |
| `TELEGRAM_BOT_TOKEN`            | yes        | `123456:ABC…`                | BotFather token.                                     |
| `TELEGRAM_CHAT_ID`              | yes        | `@mychannel`                 | Target chat/channel.                                 |
| `X_API_KEY` … `X_ACCESS_SECRET` | yes        | —                            | Twitter v2 keys with **write** perm.                 |

> **Laptop spec:** any 4‑core CPU, **8 GB RAM** (local 7B q4). Without GPU expect ≈ 2–5 tok/s.

---

## 3 · Architecture

```
React UI  ─────▶ FastAPI  ──┬── crewAI Writer
          WebSocket        ├── crewAI Editor
                           └── crewAI Scheduler
                               │   ▲
                               ▼   │ Celery (Redis broker)
                           SQLite  │
                           + DuckDB│(optional analytics)
```

* **LLM wrapper** (`llm_provider.py`) switches at runtime:

  * **local →** ctransformers  |  Ollama  |  LM Studio OpenAI‑compatible endpoint
  * **openai →** official OpenAI SDK
  * **hf\_api →** Hugging Face text‑generation‑inference
* **crewAI** coordinates roles; LiteLLM is the adapter for all model calls.
* **SQLite** stores posts, agent configs, schedule; **DuckDB** (optional) mirrors data for heavy analytics.

---

## 4 · Roadmap (24 weeks, 3‑person team)

| Phase                | Span     | Goals                                                                                | Issues (#)          |
| -------------------- | -------- | ------------------------------------------------------------------------------------ | ------------------- |
| **0 Bootstrap**      | wk 1     | Repo, CI, Docker skeleton, health check.                                             | BE‑1 FE‑1 DEV‑OPS‑1 |
| **1 MVP**            | wk 2‑5   | Google One‑Tap login; Writer + Scheduler; instant post to X & TG.                    | BE‑10 FE‑8          |
| **2 Model switcher** | wk 6‑7   | Implement `MODEL_PROVIDER` tri‑mode; docs for Ollama/LM Studio; add editor agent.    | BE‑5 DOC‑2          |
| **3 Scheduling**     | wk 8‑11  | Calendar UI (react-big-calendar); Celery beat; failure retries.                      | FE‑6 BE‑6 QA‑2      |
| **4 Analytics**      | wk 12‑15 | Metrics collector; DuckDB dashboards; Trend Analyzer agent (uses HF API web‑search). | BE‑8 FE‑4           |
| **5 Brand Voice**    | wk 16‑19 | Brand Editor agent (Guidance templates); user profile UI.                            | NLP‑5 FE‑3          |
| **6 Self‑improve**   | wk 20‑24 | DSPy opt‑in run to auto‑tune Writer prompts; AgentOps observability integration.     | BE‑6 MLOPS‑4        |

> See **/docs/ISSUES.md** for atomised tasks with acceptance criteria.

---

## 5 · Task template (GitHub Issues)

```text
feat(writer): support hashtag suggestions
------------------------------------------------
**Why**
Tweets perform better with 2‑3 relevant hashtags.

**Definition of Done**
- [ ] Writer adds 1‑3 hashtags at end of post when platform=="twitter".
- [ ] E‑2‑E test covers RU and EN prompts.

**Estimate**: 3 h
```

---

## 6 · Tooling rationale

| Problem                   | Chosen tool               | Why optimal                                                       |
| ------------------------- | ------------------------- | ----------------------------------------------------------------- |
| Lightweight local DB      | **SQLite WAL**            | Single‑file, ACID, JSON1, zero admin.                             |
| Analytics queries         | **DuckDB** (opt.)         | Columnar scans ≫ SQLite for aggregates, same embedded workflow.   |
| Multi‑agent orchestration | **crewAI 0.10 + LiteLLM** | Simple role schema, no heavy LangChain overhead, easy to extend.  |
| Observability             | **AgentOps** (opt‑in)     | One‑line integration, OpenTelemetry export, free tier.            |
| Local LLM                 | **ctransformers + GGUF**  | Pure‑Python, CPU optimised, 0 setup; or run via Ollama/LM Studio. |
| API LLM                   | **OpenAI / HF Inference** | Drop‑in by ENV, no code change.                                   |

---

## 7 · Contributing

1. Fork → branch → PR (Conventional Commits).
2. Ensure `pytest`, `npm test` and `docker compose up` all pass.
3. New endpoints require OpenAPI docs + unit tests.

MIT Licence — **share & build in public!**

