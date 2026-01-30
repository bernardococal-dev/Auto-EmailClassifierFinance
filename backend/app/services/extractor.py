import re

# Simple regex-based extraction functions for MVP

def extract_financial_data(text: str, attachments: list[dict] | None = None, tipo: str = 'OUTROS') -> dict:
    result = {}
    t = text or ''
    if tipo == 'NOTA_FISCAL':
        # very simple patterns, refine as needed
        fornecedor = re.search(r'Fornecedor: *(.+)', t, re.IGNORECASE)
        cnpj = re.search(r'([0-9]{2}\.?[0-9]{3}\.?[0-9]{3}/[0-9]{4}-[0-9]{2})', t)
        numero = re.search(r'Nota Fiscal\s*[:#]?\s*([0-9\-\/]+)', t, re.IGNORECASE)
        valor = re.search(r'Valor(?: Total)?[:\s]*R?\$?\s*([0-9.,]+)', t, re.IGNORECASE)
        if fornecedor:
            result['fornecedor'] = fornecedor.group(1).strip()
        if cnpj:
            result['cnpj'] = cnpj.group(1)
        if numero:
            result['numero_documento'] = numero.group(1)
        if valor:
            result['valor'] = valor.group(1).replace('.', '').replace(',', '.')

    elif tipo == 'REQUISICAO_COMPRA':
        numero = re.search(r'Requisi[cç][aã]o(?: de Compra)?\s*[:#]?\s*([0-9\-]+)', t, re.IGNORECASE)
        solicitante = re.search(r'Solicitante: *(.+)', t, re.IGNORECASE)
        valor = re.search(r'Valor Estimado[:\s]*R?\$?\s*([0-9.,]+)', t, re.IGNORECASE)
        if numero:
            result['numero_documento'] = numero.group(1)
        if solicitante:
            result['solicitante'] = solicitante.group(1).strip()
        if valor:
            result['valor'] = valor.group(1).replace('.', '').replace(',', '.')

    return result
