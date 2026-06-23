import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from montar_area_comum import (
    resumo_area_comum, linha_sinalizacao, montar_area_comum, VALOR_LOGO_ILUMINADO,
)


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
