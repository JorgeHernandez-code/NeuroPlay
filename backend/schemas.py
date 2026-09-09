from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class QuizItem(BaseModel):
    pregunta: str
    respuesta: str


class QuizSubmit(BaseModel):
    nombre: str = Field(..., min_length=2)
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = None
    fuente: Optional[str] = "web"
    respuestas: List[QuizItem] = Field(..., min_length=1)


class ChatIn(BaseModel):
    lead_id: int
    mensaje: str = Field(..., min_length=1)


class QuizResult(BaseModel):
    ok: bool
    lead_id: int
    puntaje: int
    estado: str


class ChatOut(BaseModel):
    reply: str


class LeadOut(BaseModel):
    # The ORM columns are PascalCase; map them to snake_case for the API.
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(validation_alias="Id")
    nombre: str = Field(validation_alias="Nombre")
    email: Optional[str] = Field(default=None, validation_alias="Email")
    whatsapp: Optional[str] = Field(default=None, validation_alias="WhatsApp")
    puntaje: int = Field(validation_alias="Puntaje")
    estado: str = Field(validation_alias="Estado")
    creado: Optional[datetime] = Field(default=None, validation_alias="CreatedAt")
