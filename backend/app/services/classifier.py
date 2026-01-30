import re

def classify_email(text: str, attachments: list[dict] | None = None) -> dict:
    """Return dict: {"tipo": "NOTA_FISCAL"|"REQUISICAO_COMPRA"|"OUTROS", "confidence": float}

    Rules (MVP):
      - If XML NF-e attachment or string 'xml' + 'NFe' in attachment name -> NOTA_FISCAL
      - If body contains 'nota fiscal' | 'nf' | 'danfe' -> NOTA_FISCAL
      - If body contains 'requisição' | 'rc' | 'pedido de compra' -> REQUISICAO_COMPRA
      - else OUTROS
    """
    t = (text or '').lower()
    attachments = attachments or []

    # Detect XML NF-e
    for a in attachments:
        name = a.get('nome_arquivo', '').lower()
        if name.endswith('.xml') and ('nfe' in name or 'nf-e' in name or 'nota fiscal' in name):
            return {'tipo': 'NOTA_FISCAL', 'confidence': 0.99}

    if any(k in t for k in ['nota fiscal', 'nf', 'danfe']):
        return {'tipo': 'NOTA_FISCAL', 'confidence': 0.9}

    if any(k in t for k in ['requisição', 'rc', 'pedido de compra', 'requisicao']):
        return {'tipo': 'REQUISICAO_COMPRA', 'confidence': 0.9}

    return {'tipo': 'OUTROS', 'confidence': 0.6}
