# PulsePost AI — TDD Taskboard

> **Methodology = Red ▶ Green ▶ Refactor**
>
> • Write a failing test (RED)
> • Write minimal code to make it pass (GREEN)
> • Refactor / clean / commit
> Each micro‑task must not exceed **30 min**.
>
> Tech stack locked to 2025‑05 LTS versions:
>
> * Python 3.12 · **pytest 8** · **httpx 0.27** · **pydantic 2.7**
> * **FastAPI 0.112** · **SQLModel 0.0.16** · **crewAI 0.10.3** · **LiteLLM 0.25**
> * React 18.3 · Vite 5 · **shadcn/ui 2025.05** · Tailwind 3.5 · Jest 30
> * Celery 6.1 · Redis 7.2 (alpine)
> * ctransformers 0.3.5 + GGUF
> * Playwright 1.45 (E2E)

---

## 0 · Skeleton / CI

| ID         | Test first                                                                                 | Target code                    | Done |
| ---------- | ------------------------------------------------------------------------------------------ | ------------------------------ | ---- |
| **CI‑001** | `test_health_route_returns_ok()` → expect 200 JSON {"status":"ok"}                         | implement `/health` in FastAPI | \[ ] |
| **CI‑002** | GitHub Actions workflow asserts poetry lock passes `poetry check`, `pytest -q`, `npm test` | add `.github/workflows/ci.yml` | \[ ] |

---

## 1 · LLM Provider Abstraction

| ID          | RED phase (pytest)                                                                                             | GREEN phase (impl)                                             | Refactor hints                        |
| ----------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------- |
| **LLM‑001** | `test_local_provider_returns_str()` → call LocalProvider("ping") expect startswith "pong"                      | minimal `LocalProvider.generate()` stub returns "pong:"+prompt | move provider selection to factory    |
| **LLM‑002** | `test_openai_provider_called_with_key(monkeypatch)` → patch env `OPENAI_API_KEY` & assert `httpx.post` invoked | implement OpenAIProvider using LiteLLM                         | use dependency‑injection via settings |
| **LLM‑003** | `test_factory_returns_correct_provider()` for env `MODEL_PROVIDER=hf_api`                                      | factory in `llm_provider.py`                                   | consolidate logging, add typing       |

---

## 2 · Database Models (SQLModel + SQLite)

| ID         | Test                                                                                | Code                                                   | Notes                                             |
| ---------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------- |
| **DB‑001** | `test_post_schema_roundtrip(session)` → create Post → commit → query → fields equal | `Post` model with fields id, content, platform, status | enable WAL in engine                              |
| **DB‑002** | `test_agent_memory_insert_and_retrieve()` with JSON + embedding bytes               | `AgentMemory` model, blob field                        | use `sqlite3.register_adapter(bytes, lambda b:b)` |

---

## 3 · Writer Agent (crewAI)

| ID         | Test                                                                                             | Implementation                        | Notes                           |
| ---------- | ------------------------------------------------------------------------------------------------ | ------------------------------------- | ------------------------------- |
| **WR‑001** | `test_writer_generates_non_empty_text(monkeypatch)` → mock LLM returns "foo"                     | Writer agent class with role="Writer" | isolate via LiteLLM mock        |
| **WR‑002** | `test_writer_respects_brand_style(tmp_path)` → feed profile JSON → output contains brand tagline | pass profile into system prompt       | store profile in Settings table |

---

## 4 · Editor Agent (Guidance)

| ID         | Test                                                                          | Implementation                      | Notes             |
| ---------- | ----------------------------------------------------------------------------- | ----------------------------------- | ----------------- |
| **ED‑001** | `test_editor_removes_banned_words()` wordlist \["bad"] → ensure not in output | guidance template with regex filter | keep latency <3 s |

---

## 5 · Scheduler Agent + Celery

| ID          | Test                                                                   | Code                           | Notes                          |
| ----------- | ---------------------------------------------------------------------- | ------------------------------ | ------------------------------ |
| **SCH‑001** | `test_schedule_calculates_default_time()` => in 1 hour (freezegun)     | simple rule in Scheduler agent | later: ML optimisation         |
| **SCH‑002** | `test_publish_task_posts_to_twitter(monkeypatch)` → stub tweepy client | Celery task `publish_post`     | use `redis://localhost:6379/0` |

---

## 6 · API Endpoints

| ID          | Test (httpx.AsyncClient)                                 | Code                             | Notes                      |
| ----------- | -------------------------------------------------------- | -------------------------------- | -------------------------- |
| **API‑001** | POST `/generate` with json {topic:"hi"} → 201 & post\_id | route calls Writer & stores Post | background task for Editor |
| **API‑002** | POST `/publish/{post_id}` → 202 & status=queued          | adds job to Celery               | retry on exception         |

---

## 7 · Frontend (dark theme by default)

| ID         | Jest / RTL test                                                     | Implementation                                 | Notes                      |
| ---------- | ------------------------------------------------------------------- | ---------------------------------------------- | -------------------------- |
| **FE‑001** | `renders main layout` expects textbox & btn                         | Page.tsx with shadcn/card + textarea + buttons | Tailwind `dark` class root |
| **FE‑002** | `generate button triggers API call` mock fetch → expect called once | use TanStack Query mutation                    | add loading spinner        |
| **FE‑003** | E2E Playwright: full flow generate→publish shows toast "Posted"     | Playwright script                              | set viewport 1440×900      |

---

## 8 · Analytics & Trend Analyzer (optional phase)

| ID         | Test                                                             | Implementation                             |                                |
| ---------- | ---------------------------------------------------------------- | ------------------------------------------ | ------------------------------ |
| **AN‑001** | `store_metrics()` inserts row & DuckDB returns correct aggregate | metrics collector cron                     | DuckDB file `analytics.duckdb` |
| **TR‑001** | `test_trend_agent_returns_topic_list()` stub HF API              | TrendAnalyzer uses httpx + LiteLLM ranking | rate‑limit 1 req / h           |

---

## 9 · Continuous Refactor / Style

* Black 24.2 + Ruff 0.4 + Pre‑commit.
* Commit hook: run `pytest -q && npm test --silent`.
* Every merge → CI triggers Docker build, tags `:edge`.

```
commit-msg → conventional ‑ commit
pre‑push   → pytest + jest
```

---

## 10 · Done Definition

* 100 % unit tests pass (`pytest -q`)
* 100 % frontend unit tests pass (`npm test`)
* E2E smoke (`playwright test`) green
* `docker compose up` + curl `/health` → {"status":"ok"}

🎉 Deploy «edge» image → GitHub Container Registry on every `main` push.

