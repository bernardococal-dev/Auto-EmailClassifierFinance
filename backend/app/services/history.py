from datetime import datetime


def log_event(db, documento_id, evento, usuario=None):
    """Log a history event for a given documento_id. If documento_id is None, do nothing.
    Use documento_id when a DocumentoFinanceiro exists.
    """
    if not documento_id:
        return
    from app.db import models
    h = models.Historico(documento_id=documento_id, evento=evento, usuario=usuario)
    db.add(h)
    db.commit()


def list_history(db, documento_id):
    from app.db import models
    return db.query(models.Historico).filter(models.Historico.documento_id == documento_id).order_by(models.Historico.data_hora.desc()).all()
