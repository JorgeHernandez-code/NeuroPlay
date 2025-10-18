import json
import difflib
from typing import List, Dict, Tuple

def load_faqs(negocio_row) -> List[Dict]:
    try:
        return json.loads(negocio_row.FAQs) if negocio_row and negocio_row.FAQs else []
    except Exception:
        return []

def faq_answer(user_text: str, faqs: List[Dict]) -> Tuple[str, float]:
    """
    Devuelve (respuesta, score_similitud). Usa una similitud simple por difflib.
    """
    user = user_text.lower()
    best = ("No tengo esa info exacta. ¿Quieres agendar para ayudarte mejor?", 0.0)
    for item in faqs:
        q = item.get("q", "")
        a = item.get("a", "")
        ratio = difflib.SequenceMatcher(None, user, q.lower()).ratio()
        if ratio > best[1]:
            best = (a, ratio)
    return best

def lead_scoring(respuestas: List[Dict]) -> int:
    """
    Reglas sencillas para puntaje (0–100).
    Busca palabras en respuestas: urgencia, presupuesto, tipo de servicio.
    """
    score = 0
    txt = " ".join([r["respuesta"].lower() for r in respuestas])

    # Urgencia
    if any(w in txt for w in ["hoy", "urgente", "mañana", "inmediato"]):
        score += 35
    elif any(w in txt for w in ["esta semana", "pronto"]):
        score += 20
    else:
        score += 5

    # Presupuesto
    if any(w in txt for w in ["alto", "premium", ">500", "más de 500", "más de 1m"]):
        score += 30
    elif any(w in txt for w in ["medio", "300", "200"]):
        score += 20
    else:
        score += 10

    # Servicio específico (intención clara)
    if any(w in txt for w in ["reparación", "mantenimiento", "upgrade", "formateo"]):
        score += 25
    else:
        score += 10

    return min(score, 100)

def estado_from_score(score: int) -> str:
    if score >= 70:
        return "caliente"
    if score >= 40:
        return "tibio"
    return "frio"
