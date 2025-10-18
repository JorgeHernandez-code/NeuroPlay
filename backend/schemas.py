from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class QuizItem(BaseModel):
    pregunta: str
    respuesta: str

class QuizSubmit(BaseModel):
    nombre: str = Field(..., min_length=2)
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = None
    fuente: Optional[str] = "web"
    respuestas: List[QuizItem]

class ChatIn(BaseModel):
    lead_id: int
    mensaje: str

class LeadOut(BaseModel):
    id: int
    nombre: str
    email: Optional[str]
    whatsapp: Optional[str]
    puntaje: int
    estado: str

    class Config:
        from_attributes = True
