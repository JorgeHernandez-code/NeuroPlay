# Neuro Play

Lead-generation demo for a computer repair / IT services business. A visitor
takes a short **interactive quiz**, gets scored as a **hot / warm / cold lead**,
and can then chat with a **24/7 FAQ assistant**. Captured leads show up in a
simple dashboard.

Built as a full-stack MVP: **FastAPI + SQLAlchemy** backend, **vanilla
HTML/CSS/JS** frontend, **SQLite** out of the box (swappable for Postgres or SQL
Server via one env var).

---

## Features

| Area | What it does |
| --- | --- |
| **Quiz → Lead** | `POST /api/quiz/submit` stores the lead + answers and computes a 0–100 score |
| **Lead scoring** | Rule-based scoring on urgency, budget and service intent → `caliente` / `tibio` / `frio` |
| **FAQ assistant** | `POST /api/chat` matches the question against a per-business FAQ knowledge base (fuzzy ratio + keyword overlap) and offers to book a call when confidence is low |
| **Leads dashboard** | `GET /api/leads` + a table in the UI |
| **Auto-seed** | On first run the DB is seeded with a demo business and 8 FAQs so the chat works immediately |
| **Single origin** | The backend also serves the frontend, so one command runs the whole app |

## Tech stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn
- **Frontend:** static HTML/CSS/JS (no build step)
- **Database:** SQLite by default; any SQLAlchemy URL via `DATABASE_URL`
- **Tests:** pytest + FastAPI `TestClient`
- **CI:** GitHub Actions runs the test suite on every push

## Project layout

```
backend/
  main.py         FastAPI app + routes, serves the frontend, startup seed
  database.py     Engine/session config (SQLite default, DATABASE_URL override)
  models.py       SQLAlchemy models: Negocio, Leads, QuizRespuestas, Mensajes
  schemas.py      Pydantic request/response models
  ai.py           Lead scoring + FAQ matching (no external AI service)
  seed.py         Demo business + FAQ knowledge base
  tests/          pytest suite
frontend/
  index.html      Landing page: quiz, chat, leads table
  app.js          Fetch calls + DOM logic
  Style.css       Styles
```

## Run locally

Requires Python 3.11+.

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000> — the page, the API and the docs
(<http://127.0.0.1:8000/docs>) are all on the same port.

No configuration needed: a `backend/neuroplay.db` SQLite file is created and
seeded automatically.

## Run the tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## Configuration

All optional — see [`backend/.env.example`](backend/.env.example). Copy it to
`backend/.env` to override.

| Variable | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///backend/neuroplay.db` | Any SQLAlchemy URL (Postgres, MySQL, …) |
| `SQLSERVER_SERVER` etc. | — | Alternative: build a SQL Server URL from parts (needs `pip install pyodbc`) |

## API reference

| Method | Path | Body | Response |
| --- | --- | --- | --- |
| `GET` | `/api/health` | — | `{ "ok": true }` |
| `POST` | `/api/quiz/submit` | `{ nombre, email?, whatsapp?, respuestas: [{pregunta, respuesta}] }` | `{ ok, lead_id, puntaje, estado }` |
| `POST` | `/api/chat` | `{ lead_id, mensaje }` | `{ reply }` |
| `GET` | `/api/leads` | — | `[{ id, nombre, email, whatsapp, puntaje, estado, creado }]` |

## Possible next steps

- Replace the rule-based FAQ matcher with embeddings / an LLM
- Auth for the leads dashboard
- Persist the full chat transcript per lead in the UI
- Dockerfile + deploy config

## License

MIT — see [LICENSE](LICENSE).
