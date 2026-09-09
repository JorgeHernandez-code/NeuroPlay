"""Seed the database with a demo business + FAQ knowledge base.

Runs automatically on app startup (only if the Negocio table is empty) so the
chat assistant has something to answer with. Safe to run multiple times.
"""
import json

from sqlalchemy.orm import Session

from models import Negocio

DEMO_FAQS = [
    {"q": "cuales son los horarios de atencion", "a": "Atendemos de lunes a sabado de 9:00 a 19:00."},
    {"q": "tienen servicio a domicilio", "a": "Si, ofrecemos servicio a domicilio dentro de la ciudad con un cargo adicional."},
    {"q": "que garantia dan en las reparaciones", "a": "Todas las reparaciones incluyen 90 dias de garantia sobre la mano de obra y los repuestos."},
    {"q": "cuanto cuesta un diagnostico", "a": "El diagnostico tiene un costo de 15 USD que se descuenta si aceptas la reparacion."},
    {"q": "cuanto tarda una reparacion", "a": "La mayoria de reparaciones se entregan en 24 a 48 horas segun el repuesto."},
    {"q": "aceptan tarjeta de credito", "a": "Aceptamos efectivo, transferencia y tarjetas de credito/debito."},
    {"q": "hacen mantenimiento preventivo", "a": "Si, el mantenimiento preventivo incluye limpieza interna, cambio de pasta termica y optimizacion del sistema."},
    {"q": "donde estan ubicados", "a": "Estamos en el centro de la ciudad. Te compartimos la ubicacion exacta al agendar."},
]


def seed(db: Session) -> None:
    if db.query(Negocio).first():
        return

    db.add(
        Negocio(
            Nombre="Neuro Play Tech",
            Rubro="Reparacion y mantenimiento de computadoras",
            Brief=(
                "Taller tecnico especializado en reparacion, mantenimiento y "
                "upgrades de laptops y PCs de escritorio."
            ),
            FAQs=json.dumps(DEMO_FAQS, ensure_ascii=False),
            UrlCalendly="https://calendly.com/neuroplay-demo/asesoria",
        )
    )
    db.commit()
