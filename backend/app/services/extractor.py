import re
import json

# Enhanced extraction that adapts based on subtype

def extract_financial_data(text: str, attachments: list[dict] | None = None, tipo: str = 'OUTROS', subtipo: str | None = None) -> dict:
    result = {}
    t = text or ''
    attachments = attachments or []

    # Common fields
    fornecedor = re.search(r'Fornecedor[:\s]*[:\-]? *(.+)', t, re.IGNORECASE)
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

    # Subtype-specific extraction
    if subtipo == 'NF_FRETE':
        # transportadora, origem, destino (heuristic)
        transportadora = re.search(r'Transportadora[:\s]*(.+)', t, re.IGNORECASE)
        origem = re.search(r'Origem[:\s]*(.+)', t, re.IGNORECASE)
        destino = re.search(r'Destino[:\s]*(.+)', t, re.IGNORECASE)
        if transportadora:
            result['transportadora'] = transportadora.group(1).strip()
        if origem:
            result['origem'] = origem.group(1).strip()
        if destino:
            result['destino'] = destino.group(1).strip()

    if subtipo == 'NF_SERVICO':
        iss = re.search(r'ISS[:\s]*([0-9.,]+)', t, re.IGNORECASE)
        cnae = re.search(r'CNAE[:\s]*([0-9\-]+)', t, re.IGNORECASE)
        if iss:
            result['iss'] = iss.group(1)
        if cnae:
            result['cnae'] = cnae.group(1)

    if subtipo == 'NF_PRODUTO':
        ncm = re.search(r'NCM[:\s]*([0-9]{2,8})', t, re.IGNORECASE)
        itens = re.findall(r'(?:Item|Produto)[:\s]*([A-Za-z0-9\s\-_,]+)\s+Quantidade[:\s]*([0-9]+)', t, re.IGNORECASE)
        if ncm:
            result['ncm'] = ncm.group(1)
        if itens:
            result['itens'] = [{'descricao': i[0].strip(), 'quantidade': int(i[1])} for i in itens]

    if subtipo == 'NF_MATERIAL_INTERNO':
        # mark as internal usage
        result['material_interno'] = True

    return result

