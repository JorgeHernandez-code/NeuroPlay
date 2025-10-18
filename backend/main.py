from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import Base, engine, get_db
from models import Lead, QuizRespuesta, Mensaje, Negocio
from schemas import QuizSubmit, ChatIn, LeadOut
from ai import load_faqs, faq_answer, lead_scoring, estado_from_score

# No hace falta crear tablas porque ya las hicimos vía SQL,
# pero si quieres que SQLAlchemy valide/cree ausentes:
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Neuro Play API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción restringe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/leads", response_model=List[LeadOut])
def list_leads(db: Session = Depends(get_db)):
    rows = db.query(Lead).order_by(Lead.Id.desc()).limit(100).all()
    return rows

@app.post("/api/quiz/submit")
def submit_quiz(payload: QuizSubmit, db: Session = Depends(get_db)):
    # Crear lead
    lead = Lead(
        Nombre=payload.nombre,
        Email=payload.email,
        WhatsApp=payload.whatsapp,
        Fuente=payload.fuente,
    )
    db.add(lead)
    db.flush()  # para obtener Id

    # Guardar respuestas
    for r in payload.respuestas:
        db.add(QuizRespuesta(LeadId=lead.Id, Pregunta=r.pregunta, Respuesta=r.respuesta))

    # Scoring
    resp_list = [{"pregunta": r.pregunta, "respuesta": r.respuesta} for r in payload.respuestas]
    score = lead_scoring(resp_list)
    lead.Puntaje = score
    lead.Estado = estado_from_score(score)

    db.commit()
    return {"ok": True, "lead_id": lead.Id, "puntaje": score, "estado": lead.Estado}

@app.post("/api/chat")
def chat(payload: ChatIn, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.Id == payload.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    # Guarda mensaje del usuario
    db.add(Mensaje(LeadId=lead.Id, Canal="web", Direccion="in", Texto=payload.mensaje))

    negocio = db.query(Negocio).order_by(Negocio.Id.asc()).first()
    faqs = load_faqs(negocio)
    resp, sim = faq_answer(payload.mensaje, faqs)

    # Si similitud baja, ofrecer agendar
    if sim < 0.45:
        extra = f" ¿Quieres agendar una asesoría? {negocio.UrlCalendly}" if negocio and negocio.UrlCalendly else ""
        resp = f"{resp}{extra}"

    # Guarda respuesta del bot
    db.add(Mensaje(LeadId=lead.Id, Canal="web", Direccion="out", Texto=resp))
    db.commit()
    return {"reply": resp}
