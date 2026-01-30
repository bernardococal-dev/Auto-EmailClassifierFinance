from datetime import datetime
from app.db import models


def log_event(db, documento_id, evento, usuario=None):
    h = models.Historico(documento_id=documento_id, evento=evento, usuario=usuario)
    db.add(h)
    db.commit()


def list_history(db, documento_id):
    return db.query(models.Historico).filter(models.Historico.documento_id == documento_id).order_by(models.Historico.data_hora.desc()).all()
