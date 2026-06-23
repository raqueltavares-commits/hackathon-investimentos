import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from montar_area_comum import (
    resumo_area_comum, linha_sinalizacao, montar_area_comum, VALOR_LOGO_ILUMINADO,
    linha_numero_porta, linha_quadros_marketing,
    VALOR_NUMERO_PORTA, VALOR_QUADRO_MARKETING, QUADROS_POR_PAVIMENTO,
)


def test_numero_porta_por_unidades():
    l = linha_numero_porta(44)
    assert l.categoria == "SINALIZAÇÃO"
    assert l.quantidade == 44
    assert l.valor_unitario == VALOR_NUMERO_PORTA == 150.0
    assert l.total_linha == 6600.0


def test_quadros_marketing_por_pavimento():
    # 4 quadros por pavimento × R$150
    l = linha_quadros_marketing(11)
    assert l.quantidade == 11 * QUADROS_POR_PAVIMENTO == 44
    assert l.valor_unitario == VALOR_QUADRO_MARKETING == 150.0
    assert l.total_linha == 6600.0


def test_montar_area_comum_sinalizacao_auto_unidades_e_pavimentos():
    payload = {
        "spot": "X", "tem_decor": False,
        "total_unidades": 44, "total_pavimentos": 11,
        "ambientes": [{"nome": "Recepção", "linhas": [
            {"categoria": "MOBILIÁRIO", "item": "Sofá", "quantidade": 1, "valor_unitario": 1000.0}]}],
        "sinalizacao": [{"ambiente": "Recepção", "qtd": 1}],
    }
    res = montar_area_comum(payload)
    sin = next(a for a in res["abas"] if a["nome"] == "Sinalização")
    flat = [c for r in sin["rows"] for c in r]
    assert any("Números" in str(c) or "porta" in str(c).lower() for c in flat)
    assert any("marketing" in str(c).lower() or "quadro" in str(c).lower() for c in flat)
    # subtotal sinalização = logo 2500 + portas 44×150 (6600) + quadros 44×150 (6600) = 15700
    sub = next(a["subtotal"] for a in res["resumo"]["abas"] if a["nome"] == "Sinalização")
    assert sub == 2500.0 + 6600.0 + 6600.0


def test_resumo_soma_subtotais_adm_e_decor():
    r = resumo_area_comum([("Recepção", 30000.0), ("Rooftop", 70000.0)],
                          tem_decor=True, budget=None)
    assert r["subtotal"] == 100000.0
    assert r["taxa_adm"] == 13000.0
    assert r["taxa_decor"] == 6000.0
    assert r["total"] == 119000.0


def test_resumo_sem_decor_zera_decor():
    r = resumo_area_comum([("Recepção", 10000.0)], tem_decor=False, budget=None)
    assert r["taxa_decor"] == 0.0
    assert r["total"] == round(10000.0 * 1.13, 2)


def test_resumo_budget_calcula_saldo():
    r = resumo_area_comum([("Recepção", 100000.0)], tem_decor=True, budget=150000.0)
    assert r["budget"] == 150000.0
    assert r["saldo"] == round(150000.0 - r["total"], 2)


def test_resumo_sem_budget_saldo_none():
    r = resumo_area_comum([("Recepção", 100.0)], tem_decor=True, budget=None)
    assert r["saldo"] is None


def test_linha_sinalizacao_logo_iluminado():
    l = linha_sinalizacao("Recepção", qtd=1)
    assert l.categoria == "SINALIZAÇÃO"
    assert l.valor_unitario == VALOR_LOGO_ILUMINADO == 2500.0
    assert l.total_linha == 2500.0
    assert "logo iluminado" in l.item.lower()


def test_marcenaria_m2_precifica_por_area():
    payload = {
        "spot": "X", "tem_decor": False,
        "ambientes": [{"nome": "Recepção", "linhas": [
            {"categoria": "MARCENARIA", "item": "Painel MDF", "marcenaria_m2": 9.76}]}],
    }
    res = montar_area_comum(payload)
    # subtotal Recepção = 9,76 × 2000 = 19520
    assert res["resumo"]["abas"][0]["subtotal"] == 19520.0


def test_montar_area_comum_estrutura():
    payload = {
        "spot": "Rosa Sul Spot", "tem_decor": True, "budget": 150000.0,
        "ambientes": [
            {"nome": "Recepção", "linhas": [
                {"categoria": "MOBILIÁRIO", "item": "Sofá", "quantidade": 1,
                 "valor_unitario": 2000.0, "frete": 100.0}]},
        ],
        "sinalizacao": [{"ambiente": "Recepção", "qtd": 1}],
        "servicos": [{"item": "Instalações elétricas", "quantidade": 4, "valor_unitario": 700.0}],
    }
    res = montar_area_comum(payload)
    nomes = [a["nome"] for a in res["abas"]]
    assert "Recepção" in nomes
    assert "Sinalização" in nomes
    assert "Serviços e Instalações" in nomes
    # Resumo: subtotal = sofá c/ frete (2100) + logo (2500) + serviços (2800) = 7400
    assert res["resumo"]["subtotal"] == 7400.0
    assert res["resumo"]["taxa_adm"] == round(7400.0 * 0.13, 2)
    assert res["resumo"]["budget"] == 150000.0
    # cada aba tem matriz de 11 colunas
    for a in res["abas"]:
        assert all(len(r) == 11 for r in a["rows"])
