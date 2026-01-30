from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app import schemas
from app.services.history import log_event, list_history
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os

router = APIRouter()

LOCAL_TZ = os.environ.get('LOCAL_TZ', 'UTC')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.DocumentoOut])
def list_documentos(tipo: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.DocumentoFinanceiro)
    if tipo:
        q = q.filter(models.DocumentoFinanceiro.tipo == tipo)
    if status:
        q = q.filter(models.DocumentoFinanceiro.status == status)
    docs = q.all()
    return docs

@router.get("/{documento_id}", response_model=schemas.DocumentoDetail)
def get_documento(documento_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.DocumentoFinanceiro).filter(models.DocumentoFinanceiro.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    # Attach historico and anexos (via Email)
    historicos = list_history(db, doc.id)
    email = db.query(models.Email).filter(models.Email.id == doc.email_id).first()
    anexos = email.anexos if email else []

    resp = {
        'id': doc.id,
        'email_id': doc.email_id,
        'tipo': doc.tipo.value,
        'subtipo': doc.subtipo.value if doc.subtipo else None,
        'fornecedor': doc.fornecedor,
        'cnpj': doc.cnpj,
        'numero_documento': doc.numero_documento,
        'valor': float(doc.valor) if doc.valor is not None else None,
        'metadados': (None if not doc.metadados else __import__('json').loads(doc.metadados)),
        'status': doc.status.value,
        'confirmado_em': doc.confirmado_em,
        'confirmado_por': doc.confirmado_por,
        'historicos': historicos,
        'anexos': anexos,
    }
    return resp

@router.post("/{documento_id}/confirmar")
def confirmar_documento(documento_id: str, usuario: str, db: Session = Depends(get_db)):
    doc = db.query(models.DocumentoFinanceiro).filter(models.DocumentoFinanceiro.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    if doc.status == models.DocumentStatus.FEITO:
        raise HTTPException(status_code=400, detail="Documento já está marcado como FEITO")
    doc.status = models.DocumentStatus.FEITO
    try:
        tz = ZoneInfo(LOCAL_TZ)
        doc.confirmado_em = datetime.now(tz=tz)
    except Exception:
        doc.confirmado_em = datetime.now(tz=timezone.utc)
    doc.confirmado_por = usuario
    db.add(doc)
    db.commit()
    log_event(db, doc.id, "Marcar como FEITO", usuario)
    return {"status": "ok"}

@router.get("/{documento_id}/email-original")
def get_email_link(documento_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.DocumentoFinanceiro).filter(models.DocumentoFinanceiro.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    email = db.query(models.Email).filter(models.Email.id == doc.email_id).first()
    return {"link": email.link_email_original if email else None}
