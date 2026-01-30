from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class AnexoOut(BaseModel):
    id: UUID
    nome_arquivo: str
    tipo: str
    caminho_arquivo: str
    preview_imagem: Optional[str]
    criado_em: datetime

    class Config:
        orm_mode = True

class HistoricoOut(BaseModel):
    id: UUID
    evento: str
    usuario: Optional[str]
    data_hora: datetime

    class Config:
        orm_mode = True

class DocumentoOut(BaseModel):
    id: UUID
    tipo: str
    fornecedor: Optional[str]
    cnpj: Optional[str]
    numero_documento: Optional[str]
    valor: Optional[float]
    status: str
    confirmado_em: Optional[datetime]
    confirmado_por: Optional[str]

    class Config:
        orm_mode = True

class DocumentoDetail(DocumentoOut):
    email_id: UUID
    historico: List[HistoricoOut] | None = None
    anexos: List[AnexoOut] | None = None

    class Config:
        orm_mode = True
