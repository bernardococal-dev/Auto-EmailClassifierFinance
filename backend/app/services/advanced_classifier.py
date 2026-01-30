import re
from typing import List

# Helper utilities

def _norm(text: str) -> str:
    return (text or '').lower()


def _has_any(text: str, keywords: List[str]) -> bool:
    t = _norm(text)
    return any(k.lower() in t for k in keywords)


def _filename_has_any(name: str, keywords: List[str]) -> bool:
    return any(k.lower() in (name or '').lower() for k in keywords)


def is_requisicao_compra(text: str, remetente: str, attachments: List[dict]) -> float:
    t = _norm(text)
    score = 0.0
    keywords = ['requisição de compra', 'requisicao de compra', 'rc', 'pedido interno', 'pedido de compra', 'solicitação de compra', 'solicitacao de compra']
    if _has_any(t, keywords):
        score += 0.8
    # remetente internal heuristic (contains company domain) - basic: if no '@' or contains 'empresa' keyword
    if remetente and ('@' in remetente) and remetente.endswith('@empresa.com'):
        score += 0.1
    # absence of xml fiscal increases chance (weak)
    if not any(a.get('nome_arquivo','').lower().endswith('.xml') for a in attachments):
        score += 0.05
    return min(score, 0.99)


def is_nf_frete(text: str, attachments: List[dict]) -> float:
    t = _norm(text)
    score = 0.0
    keywords = ['frete', 'transporte', 'ct-e', 'ct-e', 'conhecimento de transporte', 'cte', 'carga']
    if _has_any(t, keywords):
        score += 0.6    # explicit CT-e mention in text gives high confidence
    if 'ct-e' in t or 'cte' in t or 'conhecimento de transporte' in t:
        score = max(score, 0.9)    # XML CT-e detection
    for a in attachments or []:
        name = a.get('nome_arquivo','').lower()
        if name.endswith('.xml') and ('cte' in name or 'conhecimento' in name or 'ct-e' in name):
            score = max(score, 0.95)
    # transportadora as remetente (heuristic: 'transportadora' word)
    if _has_any(t, ['transportadora']):
        score += 0.2
    return min(score, 0.99)


def is_nf_servico(text: str, attachments: List[dict]) -> float:
    t = _norm(text)
    score = 0.0
    if _has_any(t, ['serviço', 'prestação de serviço', 'prestacao de servico', 'mão de obra', 'mao de obra']):
        score += 0.7
    # presence of 'ISS' or 'issqn' or 'NFS-e'
    if _has_any(t, ['iss', 'issqn', 'nfse', 'nfs-e', 'nfs']):
        score = max(score, 0.9)
    # absence of NCM (product code) supports service
    if 'ncm' not in t:
        score += 0.05
    return min(score, 0.99)


def is_nf_produto(text: str, attachments: List[dict]) -> float:
    t = _norm(text)
    score = 0.0
    if _has_any(t, ['produto', 'mercadoria', 'item', 'itens']):
        score += 0.4
    # NCM detection (8 digits or 'ncm')
    if re.search(r'\b[0-9]{8}\b', t) or 'ncm' in t:
        score += 0.5
    # quantity / valor unitario
    if _has_any(t, ['quantidade', 'qtd', 'valor unitario', 'valor unitário']):
        score += 0.2
    # XML NF-e detection
    for a in attachments or []:
        name = a.get('nome_arquivo','').lower()
        if name.endswith('.xml') and ('nfe' in name or 'nf-e' in name or 'nota fiscal' in name):
            score = max(score, 0.95)
    return min(score, 0.99)


def is_nf_material_interno(text: str, remetente: str, attachments: List[dict]) -> float:
    t = _norm(text)
    score = 0.0
    if _has_any(t, ['material de consumo', 'manutenção', 'manutencao', 'uso interno', 'consumo']):
        score += 0.7
    # Check for supplier hints (maintenance, limpeza, ti)
    if _has_any(t, ['manutenção', 'limpeza', 'ti', 'tecnico', 'manutencao']):
        score += 0.15
    return min(score, 0.95)


def classify_email(text: str, attachments: List[dict] | None = None, remetente: str | None = None) -> dict:
    """Return {'tipo':..., 'subtipo':..., 'confidence': float}

    Order of checks/priority is important as per spec.
    """
    attachments = attachments or []
    t = _norm(text)

    # 1) Requisição de Compra (ENTRADA_INTERNA / REQUISICAO_COMPRA)
    req_score = is_requisicao_compra(t, remetente or '', attachments)
    if req_score >= 0.6:
        return {'tipo': 'ENTRADA_INTERNA', 'subtipo': 'REQUISICAO_COMPRA', 'confidence': round(req_score, 2)}

    # 2) NF Frete (high priority)
    frete_score = is_nf_frete(t, attachments)
    if frete_score >= 0.8:
        return {'tipo': 'DOCUMENTO_FORNECEDOR', 'subtipo': 'NF_FRETE', 'confidence': round(frete_score, 2)}

    # 3) NF Serviço
    serv_score = is_nf_servico(t, attachments)
    if serv_score >= 0.8:
        return {'tipo': 'DOCUMENTO_FORNECEDOR', 'subtipo': 'NF_SERVICO', 'confidence': round(serv_score, 2)}

    # 4) NF Produto
    prod_score = is_nf_produto(t, attachments)
    if prod_score >= 0.8:
        return {'tipo': 'DOCUMENTO_FORNECEDOR', 'subtipo': 'NF_PRODUTO', 'confidence': round(prod_score, 2)}

    # 5) NF Material Interno
    mat_score = is_nf_material_interno(t, remetente or '', attachments)
    if mat_score >= 0.8:
        return {'tipo': 'DOCUMENTO_FORNECEDOR', 'subtipo': 'NF_MATERIAL_INTERNO', 'confidence': round(mat_score, 2)}

    # fallback: if some score is moderate, return best guess with lower confidence
    best = max([
        ('ENTRADA_INTERNA', 'REQUISICAO_COMPRA', req_score),
        ('DOCUMENTO_FORNECEDOR', 'NF_FRETE', frete_score),
        ('DOCUMENTO_FORNECEDOR', 'NF_SERVICO', serv_score),
        ('DOCUMENTO_FORNECEDOR', 'NF_PRODUTO', prod_score),
        ('DOCUMENTO_FORNECEDOR', 'NF_MATERIAL_INTERNO', mat_score),
    ], key=lambda x: x[2])

    tipo, subtipo, score = best
    return {'tipo': tipo, 'subtipo': subtipo, 'confidence': round(score, 2)}
