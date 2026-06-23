import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from montar_orcamento import (
    itens_para_tipologia, montar_memorial, serializar_estruturado,
)

PV: dict = {}


def _linhas(cap, terraco, tipo="Padrão"):
    return itens_para_tipologia(cap, terraco, tipo, PV)


def test_itens_tem_ambiente_e_acabamento():
    linhas = _linhas(2, "Sem")
    gab = next(l for l in linhas if "gabinete inferior" in l.item.lower())
    assert gab.ambiente == "Cozinha"
    assert gab.acabamento


def test_acabamento_varia_por_estilo():
    bio = itens_para_tipologia(2, "Sem", "Padrão", PV, estilo="biofilico")
    cln = itens_para_tipologia(2, "Sem", "Padrão", PV, estilo="clean")
    gb = next(l for l in bio if "gabinete inferior" in l.item.lower())
    gc = next(l for l in cln if "gabinete inferior" in l.item.lower())
    assert gb.acabamento != gc.acabamento


def test_servicos_presentes():
    linhas = _linhas(2, "Sem")
    assert any(l.categoria == "SERVIÇOS" for l in linhas)
    assert any("pintura" in l.item.lower() for l in linhas)


def test_jacuzzi_opcional_em_garden():
    linhas = _linhas(4, "Garden")
    jac = next(l for l in linhas if "jacuzzi" in l.item.lower())
    assert jac.opcional is True


def test_jacuzzi_fora_do_total_base():
    g = montar_memorial("A", "Garden", "Biofílico", "X", _linhas(4, "Garden"))
    s = montar_memorial("B", "Sem", "Biofílico", "X", _linhas(4, "Sem"))
    assert g.total_geral == s.total_geral
    assert g.total_com_jacuzzi > g.total_geral
    assert round(g.total_com_jacuzzi - g.total_geral, 2) == g.valor_opcionais


def test_serializar_estruturado_cabecalho():
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Biofílico", "Bonito Spot", _linhas(2, "Sem"))
    rows = serializar_estruturado(m, "biofilico")
    header = next(r for r in rows if "AMBIENTE" in r)
    assert "CATEGORIA" in header
    assert "COR DE ACABAMENTO" in header
    assert "FRETE (R$)" in header
    assert "TOTAL + FRETE (R$)" in header


def test_serializar_uma_linha_por_item():
    linhas = _linhas(2, "Sem")
    m = montar_memorial("A", "Sem", "Biofílico", "X", linhas)
    rows = serializar_estruturado(m, "biofilico")
    # 1 linha por item: a coluna ITEM (índice 2) preenchida == nº de itens
    nomes_itens = {l.item for l in linhas}
    item_rows = [r for r in rows if r[2] in nomes_itens]
    assert len(item_rows) == len(linhas)
    # todas as linhas têm 11 colunas
    assert all(len(r) == 11 for r in rows)


def test_serializar_estruturado_totais():
    m = montar_memorial("A", "Garden", "Biofílico", "X", _linhas(4, "Garden"))
    rows = serializar_estruturado(m, "biofilico")
    flat = [c for r in rows for c in r]
    assert any("TOTAL MARCENARIA" in str(c) for c in flat)
    assert any("Taxa Decor (6%)" in str(c) for c in flat)
    assert any("sem jacuzzi" in str(c) for c in flat)
    assert any("com jacuzzi" in str(c) for c in flat)
