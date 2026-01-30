from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

MODEL_CONFIG = {"from_attributes": True}

class AnexoOut(BaseModel):
    id: UUID
    nome_arquivo: str
    tipo: str
    caminho_arquivo: str
    preview_imagem: Optional[str]
    criado_em: datetime

    model_config = MODEL_CONFIG

class HistoricoOut(BaseModel):
    id: UUID
    evento: str
    usuario: Optional[str]
    data_hora: datetime

    model_config = MODEL_CONFIG

class DocumentoOut(BaseModel):
    id: UUID
    tipo: str
    subtipo: Optional[str] = None
    fornecedor: Optional[str]
    cnpj: Optional[str]
    numero_documento: Optional[str]
    valor: Optional[float]
    metadados: Optional[dict] = None
    status: str
    confirmado_em: Optional[datetime]
    confirmado_por: Optional[str]

    model_config = MODEL_CONFIG

class DocumentoDetail(DocumentoOut):
    email_id: UUID
    historicos: List[HistoricoOut] | None = None
    anexos: List[AnexoOut] | None = None

    model_config = MODEL_CONFIG
