import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from ai import estado_from_score, faq_answer, lead_scoring, load_faqs
from database import Base, SessionLocal, engine, get_db
from models import Lead, Mensaje, Negocio, QuizRespuesta
from schemas import ChatIn, ChatOut, LeadOut, QuizResult, QuizSubmit
from seed import seed

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Neuro Play API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # demo API; tighten for production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/leads", response_model=List[LeadOut])
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).order_by(Lead.Id.desc()).limit(100).all()


@app.post("/api/quiz/submit", response_model=QuizResult)
def submit_quiz(payload: QuizSubmit, db: Session = Depends(get_db)):
    lead = Lead(
        Nombre=payload.nombre,
        Email=payload.email,
        WhatsApp=payload.whatsapp,
        Fuente=payload.fuente,
    )
    db.add(lead)
    db.flush()  # obtain lead.Id

    for r in payload.respuestas:
        db.add(QuizRespuesta(LeadId=lead.Id, Pregunta=r.pregunta, Respuesta=r.respuesta))

    resp_list = [{"pregunta": r.pregunta, "respuesta": r.respuesta} for r in payload.respuestas]
    score = lead_scoring(resp_list)
    lead.Puntaje = score
    lead.Estado = estado_from_score(score)

    db.commit()
    return QuizResult(ok=True, lead_id=lead.Id, puntaje=score, estado=lead.Estado)


@app.post("/api/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.Id == payload.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    db.add(Mensaje(LeadId=lead.Id, Canal="web", Direccion="in", Texto=payload.mensaje))

    negocio = db.query(Negocio).order_by(Negocio.Id.asc()).first()
    faqs = load_faqs(negocio)
    resp, sim = faq_answer(payload.mensaje, faqs)

    if sim < 0.45 and negocio and negocio.UrlCalendly:
        resp = f"{resp} Agenda aqui: {negocio.UrlCalendly}"

    db.add(Mensaje(LeadId=lead.Id, Canal="web", Direccion="out", Texto=resp))
    db.commit()
    return ChatOut(reply=resp)


# --- Static frontend -------------------------------------------------------
# Serve the vanilla JS frontend from the same origin as the API so there is a
# single command to run and no CORS/base-URL configuration needed.
if os.path.isdir(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

    @app.get("/")
    def index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
