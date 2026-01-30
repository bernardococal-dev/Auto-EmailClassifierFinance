import enum
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Helper to get UTC-aware now
def now_utc():
    return datetime.now(tz=timezone.utc)

class DocumentType(enum.Enum):
    DOCUMENTO_FORNECEDOR = "DOCUMENTO_FORNECEDOR"
    ENTRADA_INTERNA = "ENTRADA_INTERNA"
    OUTROS = "OUTROS"

class DocumentStatus(enum.Enum):
    RECEBIDO = "RECEBIDO"
    CLASSIFICADO = "CLASSIFICADO"
    PENDENTE = "PENDENTE"
    FEITO = "FEITO"
    REVISAO = "REVISAO"

class DocumentSubtipo(enum.Enum):
    REQUISICAO_COMPRA = "REQUISICAO_COMPRA"
    NF_PRODUTO = "NF_PRODUTO"
    NF_SERVICO = "NF_SERVICO"
    NF_FRETE = "NF_FRETE"
    NF_MATERIAL_INTERNO = "NF_MATERIAL_INTERNO"

class Email(Base):
    __tablename__ = "emails"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String, unique=True, index=True, nullable=False)
    remetente = Column(String, nullable=False)
    assunto = Column(String, nullable=True)
    corpo = Column(Text, nullable=True)
    data_hora_email = Column(DateTime(timezone=True), nullable=True)
    link_email_original = Column(String, nullable=True)
    criado_em = Column(DateTime(timezone=True), default=now_utc)

    anexos = relationship("Anexo", back_populates="email")
    documentos = relationship("DocumentoFinanceiro", back_populates="email")

class DocumentoFinanceiro(Base):
    __tablename__ = "documentos_financeiros"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id = Column(UUID(as_uuid=True), ForeignKey("emails.id"), nullable=False)
    tipo = Column(Enum(DocumentType), nullable=False)
    fornecedor = Column(String, nullable=True)
    cnpj = Column(String, nullable=True)
    numero_documento = Column(String, nullable=True)
    valor = Column(Numeric(12, 2), nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.RECEBIDO)
    subtipo = Column(Enum(DocumentSubtipo), nullable=True)
    metadados = Column(String, nullable=True)  # JSON serialized string for extra extraction
    confirmado_em = Column(DateTime(timezone=True), nullable=True)
    confirmado_por = Column(String, nullable=True)

    email = relationship("Email", back_populates="documentos")
    historicos = relationship("Historico", back_populates="documento")

class Anexo(Base):
    __tablename__ = "anexos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_id = Column(UUID(as_uuid=True), ForeignKey("emails.id"), nullable=False)
    nome_arquivo = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    caminho_arquivo = Column(String, nullable=False)
    preview_imagem = Column(Text, nullable=True)  # base64 or path
    criado_em = Column(DateTime(timezone=True), default=now_utc)

    email = relationship("Email", back_populates="anexos")

class Historico(Base):
    __tablename__ = "historicos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    documento_id = Column(UUID(as_uuid=True), ForeignKey("documentos_financeiros.id"), nullable=False)
    evento = Column(String, nullable=False)
    usuario = Column(String, nullable=True)
    data_hora = Column(DateTime(timezone=True), default=now_utc)

    documento = relationship("DocumentoFinanceiro", back_populates="historicos")
