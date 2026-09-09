import difflib
import json
import re
from typing import Dict, List, Tuple

_STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "y", "o", "a", "en", "que",
    "cual", "cuales", "como", "es", "son", "por", "para", "con", "mi", "me",
    "tu", "su", "se", "del", "al", "lo", "hay", "tienen", "tiene",
}


def _tokens(text: str) -> set:
    words = re.findall(r"[a-záéíóúñ0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def load_faqs(negocio_row) -> List[Dict]:
    try:
        return json.loads(negocio_row.FAQs) if negocio_row and negocio_row.FAQs else []
    except (json.JSONDecodeError, TypeError):
        return []


def faq_answer(user_text: str, faqs: List[Dict]) -> Tuple[str, float]:
    """Return (answer, similarity 0-1).

    Combines a fuzzy string ratio with a keyword-overlap score so short user
    questions still match longer FAQ entries.
    """
    fallback = (
        "No tengo esa informacion exacta. Puedo agendarte una asesoria para ayudarte mejor.",
        0.0,
    )
    if not faqs:
        return fallback

    user = user_text.lower().strip()
    user_tokens = _tokens(user)
    best = fallback

    for item in faqs:
        q = item.get("q", "")
        a = item.get("a", "")
        ratio = difflib.SequenceMatcher(None, user, q.lower()).ratio()

        q_tokens = _tokens(q)
        overlap = (
            len(user_tokens & q_tokens) / len(q_tokens)
            if q_tokens and user_tokens
            else 0.0
        )

        score = max(ratio, overlap)
        if score > best[1]:
            best = (a, score)

    return best


def lead_scoring(respuestas: List[Dict]) -> int:
    """Simple rule-based lead score (0-100) from quiz answers."""
    score = 0
    txt = " ".join(r["respuesta"].lower() for r in respuestas)

    # Urgency ("no urgente" must not count as urgent)
    if "no urgente" in txt or "no urgent" in txt:
        score += 5
    elif any(w in txt for w in ["hoy", "urgente", "mañana", "inmediato"]):
        score += 35
    elif any(w in txt for w in ["esta semana", "pronto"]):
        score += 20
    else:
        score += 5

    # Budget
    if any(w in txt for w in ["alto", "premium", ">500", "más de 500", "más de 1m"]):
        score += 30
    elif any(w in txt for w in ["medio", "300", "200"]):
        score += 20
    else:
        score += 10

    # Clear service intent
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
