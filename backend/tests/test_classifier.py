import pytest
from app.services.classifier import classify_email


def test_requisicao_compra_detected():
    text = "Solicitação de compra: Favor processar a requisição de compra RC-123"
    res = classify_email(text, [], 'usuario@empresa.com')
    assert res['tipo'] == 'ENTRADA_INTERNA'
    assert res['subtipo'] == 'REQUISICAO_COMPRA'
    assert res['confidence'] >= 0.6


def test_nf_frete_over_product_priority():
    text = "Conhecimento de Transporte - CT-e referente ao frete"
    res = classify_email(text, [{'nome_arquivo': 'doc1.xml'}], 'fornecedor@transportadora.com')
    assert res['tipo'] == 'DOCUMENTO_FORNECEDOR'
    assert res['subtipo'] == 'NF_FRETE'
    assert res['confidence'] > 0.8


def test_nf_servico_detected():
    text = "Prestação de serviço - ISS informado"
    res = classify_email(text, [], 'prestador@servicos.com')
    assert res['tipo'] == 'DOCUMENTO_FORNECEDOR'
    assert res['subtipo'] == 'NF_SERVICO'
    assert res['confidence'] >= 0.7


def test_nf_produto_detected_by_ncm_and_items():
    text = "NCM: 01012100\nItem: Parafuso Quantidade: 10 Valor unitario: 1.00"
    res = classify_email(text, [{'nome_arquivo': 'invoice.xml'}], 'fornecedor@fornecedor.com')
    assert res['tipo'] == 'DOCUMENTO_FORNECEDOR'
    assert res['subtipo'] == 'NF_PRODUTO'
    assert res['confidence'] >= 0.8


def test_ambiguous_low_confidence():
    text = "Este é um email curto sem informações claras"
    res = classify_email(text, [], 'unknown@ex.com')
    assert res['confidence'] < 0.8
    assert res['tipo'] in ['ENTRADA_INTERNA','DOCUMENTO_FORNECEDOR','OUTROS']
