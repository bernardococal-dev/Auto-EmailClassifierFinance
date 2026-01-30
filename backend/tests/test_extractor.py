from app.services.extractor import extract_financial_data


def test_extract_nf_frete():
    text = "Transportadora: Transp Ltda\nOrigem: SP\nDestino: RJ\nValor: R$ 500,00"
    res = extract_financial_data(text, [], 'DOCUMENTO_FORNECEDOR', 'NF_FRETE')
    assert res.get('transportadora') == 'Transp Ltda'
    assert res.get('origem') == 'SP'
    assert res.get('destino') == 'RJ'


def test_extract_nf_servico():
    text = "ISS: 50.00\nCNAE: 1234"
    res = extract_financial_data(text, [], 'DOCUMENTO_FORNECEDOR', 'NF_SERVICO')
    assert res.get('iss') == '50.00'
    assert res.get('cnae') == '1234'


def test_extract_nf_produto():
    text = "NCM: 01012100\nItem: Parafuso Quantidade: 10"
    res = extract_financial_data(text, [], 'DOCUMENTO_FORNECEDOR', 'NF_PRODUTO')
    assert res.get('ncm') == '01012100'
    assert isinstance(res.get('itens'), list)
    assert res.get('itens')[0]['quantidade'] == 10


def test_extract_material_interno():
    text = "Material de consumo: álcool" 
    res = extract_financial_data(text, [], 'DOCUMENTO_FORNECEDOR', 'NF_MATERIAL_INTERNO')
    assert res.get('material_interno') is True
