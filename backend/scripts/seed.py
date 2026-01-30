from app.db.session import SessionLocal
from app.db import models
from app.services.preview import generate_preview
import os

DB = SessionLocal()

# Create an example email and document
email = models.Email(message_id='message-1', remetente='fornecedor@example.com', assunto='NF-e', corpo='Nota Fiscal R$ 1.234,56', link_email_original='https://mail.example/message-1')
DB.add(email)
DB.commit()

# Documento: NOTA_FISCAL
doc = models.DocumentoFinanceiro(email_id=email.id, tipo=models.DocumentType.NOTA_FISCAL, fornecedor='Fornecedor X', cnpj='12.345.678/0001-90', numero_documento='12345', valor=1234.56, status=models.DocumentStatus.CLASSIFICADO)
DB.add(doc)
DB.commit()

print('Seed criado:', doc.id)
