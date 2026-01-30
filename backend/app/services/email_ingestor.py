from typing import List
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import os

from app.services.outlook_collector import fetch_outlook_emails
from app.services.classifier import classify_email
from app.services.extractor import extract_financial_data
from app.services.preview import generate_preview
from app.services.history import log_event
from app.db.session import SessionLocal
from app.db import models

LOCAL_TZ = os.environ.get('LOCAL_TZ', 'UTC')


def _parse_graph_datetime(dt_str: str) -> datetime:
    if not dt_str:
        return None
    # Graph returns ISO strings, sometimes ending with Z
    if dt_str.endswith('Z'):
        dt_str = dt_str.replace('Z', '+00:00')
    return datetime.fromisoformat(dt_str)


def _local_now() -> datetime:
    try:
        return datetime.now(tz=ZoneInfo(LOCAL_TZ))
    except Exception:
        return datetime.now(tz=timezone.utc)


class EmailIngestor:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, user_email: str, folder: str = 'Inbox'):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_email = user_email
        self.folder = folder

    def ingest(self, top: int = 50) -> List[models.Email]:
        db = SessionLocal()
        try:
            messages = fetch_outlook_emails(self.tenant_id, self.client_id, self.client_secret, self.user_email, folder=self.folder, top=top)
            ingested = []
            for m in messages:
                message_id = m.get('message_id')
                # Idempotency: skip if message_id exists
                exists = db.query(models.Email).filter(models.Email.message_id == message_id).first()
                if exists:
                    # already ingested
                    continue

                # parse datetime
                dt = _parse_graph_datetime(m.get('data_hora_email'))

                email = models.Email(
                    message_id=message_id,
                    remetente=m.get('remetente') or '',
                    assunto=m.get('assunto'),
                    corpo=m.get('corpo_preview') or '',
                    data_hora_email=dt,
                    link_email_original=m.get('webLink')
                )
                db.add(email)
                db.commit()
                db.refresh(email)

                # persist anexos
                anexos = []
                for a in m.get('attachments', []):
                    if a.get('caminho_arquivo'):
                        tipo = 'pdf' if a.get('nome_arquivo','').lower().endswith('.pdf') else 'imagem'
                        anexo = models.Anexo(
                            email_id=email.id,
                            nome_arquivo=a.get('nome_arquivo'),
                            tipo=tipo,
                            caminho_arquivo=a.get('caminho_arquivo')
                        )
                        db.add(anexo)
                        db.commit()
                        db.refresh(anexo)
                        anexos.append(anexo)

                # classification
                classification = classify_email(email.corpo, [{'nome_arquivo': x.nome_arquivo, 'caminho_arquivo': x.caminho_arquivo} for x in anexos], email.remetente)
                tipo = classification.get('tipo')
                subtipo = classification.get('subtipo')
                confidence = classification.get('confidence', 0)
                status = models.DocumentStatus.CLASSIFICADO if confidence >= 0.8 else models.DocumentStatus.PENDENTE

                doc = models.DocumentoFinanceiro(
                    email_id=email.id,
                    tipo=models.DocumentType[tipo],
                    subtipo=models.DocumentSubtipo[subtipo] if subtipo else None,
                    status=status
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

                # now that we have a documento_id, record ingestion and attachments in history
                log_event(db, doc.id, f'Email ingerido: {message_id}', usuario=None)
                for an in anexos:
                    log_event(db, doc.id, f'Anexo salvo: {an.nome_arquivo}', usuario=None)

                log_event(db, doc.id, f'Classificado como {tipo} (conf={confidence})', usuario=None)

                # extraction
                extracted = extract_financial_data(email.corpo, [{'nome_arquivo': x.nome_arquivo, 'caminho_arquivo': x.caminho_arquivo} for x in anexos], tipo, doc.subtipo.name if doc.subtipo else None)
                changed = False
                if extracted.get('fornecedor'):
                    doc.fornecedor = extracted.get('fornecedor')
                    changed = True
                if extracted.get('cnpj'):
                    doc.cnpj = extracted.get('cnpj')
                    changed = True
                if extracted.get('numero_documento'):
                    doc.numero_documento = extracted.get('numero_documento')
                    changed = True
                if extracted.get('valor'):
                    try:
                        doc.valor = float(extracted.get('valor'))
                        changed = True
                    except Exception:
                        pass
                # save any extra fields into metadados (JSON string)
                extra_meta = {k:v for k,v in extracted.items() if k not in ['fornecedor','cnpj','numero_documento','valor']}
                if extra_meta:
                    import json
                    doc.metadados = json.dumps(extra_meta)
                    changed = True
                if changed:
                    db.add(doc)
                    db.commit()
                    log_event(db, doc.id, 'Dados extraídos e salvos', usuario=None)

                # generate previews for anexos and attach to Anexo.preview_imagem
                for a in anexos:
                    path = a.caminho_arquivo
                    try:
                        preview_b64 = generate_preview(path)
                        a.preview_imagem = preview_b64
                        db.add(a)
                        db.commit()
                        log_event(db, doc.id, f'Preview gerado para {a.nome_arquivo}', usuario=None)
                    except Exception as e:
                        log_event(db, doc.id, f'Erro ao gerar preview: {e}', usuario=None)

                ingested.append(doc)
            return ingested
        finally:
            db.close()
