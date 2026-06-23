import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from revit_para_linhas import blocos_para_linhas, casar_regra, REGRAS_PADRAO

# Subconjunto real do Ático do Rosa Sul (Revit MCP).
BLOCOS_ATICO = [
    {"type_name": "freijó", "qtd": 2},
    {"type_name": "CADEIRA ALLEGRA -  PRETO", "qtd": 8},
    {"type_name": "BANQUETA CLARICE ALTA - PRETO", "qtd": 4},
    {"type_name": "POLTRONA ACAPULCO - PRETO", "qtd": 2},
    {"type_name": "frigobar vidro", "qtd": 1},
    {"type_name": "Único:3432869 : Bancada 06:Único:3432869", "qtd": 1},
    {"type_name": "Único:3432870 : Bancada 06:Único:3432870", "qtd": 1},
    {"type_name": "Marfim", "qtd": 3},  # ambíguo → não mapeado
]


def test_casar_regra_por_substring_case_insensitive():
    r = casar_regra("CADEIRA ALLEGRA -  PRETO", REGRAS_PADRAO)
    assert r is not None
    assert r["item"] == "Cadeira Allegra"
    assert r["categoria"] == "MOBILIÁRIO"


def test_casar_regra_pela_familia_quando_tipo_e_so_a_cor():
    # type_name ambíguo ("Cinza"), mas a família identifica o item (Nuta)
    r = casar_regra("Cinza", REGRAS_PADRAO, family="Cadeira Nuta Capri")
    assert r is not None and r["item"] == "Cadeira Nuta"


def test_nao_mapeado_mostra_familia_no_rotulo():
    res = blocos_para_linhas([{"type_name": "Cinza", "qtd": 2, "family": "Familia Desconhecida"}], {})
    assert any("Familia Desconhecida" in nm for nm in res["nao_mapeados"])


def test_tipo_conhecido_vira_linha_com_quantidade():
    res = blocos_para_linhas([{"type_name": "freijó", "qtd": 2}], {})
    linha = res["linhas"][0]
    assert linha.item == "Mesa de Jantar Cone Freijó"
    assert linha.quantidade == 2
    assert linha.categoria == "MOBILIÁRIO"


def test_consolida_blocos_do_mesmo_item():
    # 4 blocos "Bancada 06" distintos → uma linha com qtd 4
    blocos = [{"type_name": f"Único:{i} : Bancada 06:x", "qtd": 1} for i in range(4)]
    res = blocos_para_linhas(blocos, {})
    bancadas = [l for l in res["linhas"] if "Bancada" in l.item]
    assert len(bancadas) == 1
    assert bancadas[0].quantidade == 4


def test_preco_vem_do_catalogo_quando_tem_codigo():
    produtos = {"MOB0005": {"valor_unitario": 90.8, "cor_acabamento": "", "link": ""}}
    res = blocos_para_linhas([{"type_name": "CADEIRA ALLEGRA", "qtd": 8}], produtos)
    cad = res["linhas"][0]
    assert cad.valor_unitario == 90.8


def test_tipo_nao_mapeado_nao_some_e_e_sinalizado():
    res = blocos_para_linhas([{"type_name": "Marfim", "qtd": 3}], {})
    assert "Marfim" in res["nao_mapeados"]
    # ainda gera uma linha visível pra revisão (não some silenciosamente)
    linha = next(l for l in res["linhas"] if l.item == "Marfim")
    assert linha.categoria == "A REVISAR"
    assert linha.valor_unitario == 0.0


def test_atico_consolidado_bate_com_template():
    res = blocos_para_linhas(BLOCOS_ATICO, {})
    por_item = {l.item: l.quantidade for l in res["linhas"]}
    assert por_item["Cadeira Allegra"] == 8
    assert por_item["Banqueta Clarice Alta"] == 4
    assert por_item["Poltrona jardim Acapulco"] == 2
    assert por_item["Mesa de Jantar Cone Freijó"] == 2
    assert "Marfim" in res["nao_mapeados"]
