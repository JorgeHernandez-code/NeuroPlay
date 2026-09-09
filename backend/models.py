from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base

class Negocio(Base):
    __tablename__ = "Negocio"
    Id = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(150), nullable=False)
    Rubro = Column(String(150))
    Brief = Column(Text)
    FAQs = Column(Text)  # JSON string
    UrlCalendly = Column(String(300))
    CreatedAt = Column(DateTime, server_default=func.now())

class Lead(Base):
    __tablename__ = "Leads"
    Id = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(120), nullable=False)
    Email = Column(String(200))
    WhatsApp = Column(String(40))
    Fuente = Column(String(80))
    Puntaje = Column(Integer, default=0)
    Estado = Column(String(20), default="frio")
    CreatedAt = Column(DateTime, server_default=func.now())

    respuestas = relationship("QuizRespuesta", back_populates="lead", cascade="all, delete-orphan")
    mensajes = relationship("Mensaje", back_populates="lead", cascade="all, delete-orphan")

class QuizRespuesta(Base):
    __tablename__ = "QuizRespuestas"
    Id = Column(Integer, primary_key=True, index=True)
    LeadId = Column(Integer, ForeignKey("Leads.Id"), nullable=False)
    Pregunta = Column(String(300), nullable=False)
    Respuesta = Column(String(400), nullable=False)

    lead = relationship("Lead", back_populates="respuestas")

class Mensaje(Base):
    __tablename__ = "Mensajes"
    Id = Column(Integer, primary_key=True, index=True)
    LeadId = Column(Integer, ForeignKey("Leads.Id"), nullable=False)
    Canal = Column(String(20), nullable=False)     # 'web'
    Direccion = Column(String(5), nullable=False)  # 'in' | 'out'
    Texto = Column(Text, nullable=False)
    CreatedAt = Column(DateTime, server_default=func.now())

    lead = relationship("Lead", back_populates="mensajes")
