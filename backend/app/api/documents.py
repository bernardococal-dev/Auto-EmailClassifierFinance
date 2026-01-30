from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import models
from app import schemas
from app.services.history import log_event
from datetime import datetime

router = APIRouter()

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
    return doc

@router.post("/{documento_id}/confirmar")
def confirmar_documento(documento_id: str, usuario: str, db: Session = Depends(get_db)):
    doc = db.query(models.DocumentoFinanceiro).filter(models.DocumentoFinanceiro.id == documento_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    if doc.status == models.DocumentStatus.FEITO:
        raise HTTPException(status_code=400, detail="Documento já está marcado como FEITO")
    doc.status = models.DocumentStatus.FEITO
    doc.confirmado_em = datetime.now()
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
