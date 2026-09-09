import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use an isolated temp-file database for the test run.
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

from ai import estado_from_score, faq_answer, lead_scoring  # noqa: E402
from database import Base, engine  # noqa: E402
from main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_quiz_submit_and_score(client):
    payload = {
        "nombre": "Ada Lovelace",
        "email": "ada@example.com",
        "respuestas": [
            {"pregunta": "Que necesitas hoy", "respuesta": "Reparación"},
            {"pregunta": "Urgencia", "respuesta": "Hoy"},
            {"pregunta": "Presupuesto", "respuesta": "Alto"},
        ],
    }
    r = client.post("/api/quiz/submit", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["puntaje"] == 90
    assert data["estado"] == "caliente"

    leads = client.get("/api/leads").json()
    assert any(lead["nombre"] == "Ada Lovelace" for lead in leads)


def test_chat_flow(client):
    lead_id = client.post(
        "/api/quiz/submit",
        json={"nombre": "Grace Hopper", "respuestas": [
            {"pregunta": "Urgencia", "respuesta": "No urgente"},
        ]},
    ).json()["lead_id"]

    r = client.post("/api/chat", json={"lead_id": lead_id, "mensaje": "cuales son los horarios de atencion?"})
    assert r.status_code == 200
    assert "9:00" in r.json()["reply"]


def test_chat_unknown_lead(client):
    r = client.post("/api/chat", json={"lead_id": 999999, "mensaje": "hola"})
    assert r.status_code == 404


def test_scoring_units():
    assert lead_scoring([{"pregunta": "u", "respuesta": "no urgente"}]) == 25
    assert estado_from_score(75) == "caliente"
    assert estado_from_score(50) == "tibio"
    assert estado_from_score(10) == "frio"


def test_faq_fallback():
    _, sim = faq_answer("pregunta sin relacion alguna xyz", [{"q": "horarios", "a": "9 a 19"}])
    assert sim < 0.45
