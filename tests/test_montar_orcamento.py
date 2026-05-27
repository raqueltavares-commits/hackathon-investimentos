import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from montar_orcamento import itens_para_tipologia, montar_memorial, serializar_csv
from modelos import LinhaMemorial, MemorialTipologia, Produto

PRODUTOS_VAZIO: dict = {}


def _categorias(linhas: list[LinhaMemorial]) -> set[str]:
    return {l.categoria for l in linhas}


def _item_presente(linhas: list[LinhaMemorial], substr: str) -> bool:
    return any(substr.lower() in l.item.lower() for l in linhas)


def _qtd_de(linhas: list[LinhaMemorial], substr: str) -> int:
    return sum(l.quantidade for l in linhas if substr.lower() in l.item.lower())


# ── Itens fixos ──────────────────────────────────────────────────────────────

def test_sempre_tem_gabinete_inferior():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "gabinete inferior")

def test_sempre_tem_cama_queen():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "cama")

def test_sempre_tem_cooktop():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "cooktop")

def test_sempre_tem_categorias_obrigatorias():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    cats = _categorias(linhas)
    assert "MARCENARIA" in cats
    assert "MARMORARIA" in cats
    assert "ELETROS" in cats
    assert "LOUÇAS E METAIS" in cats


# ── Sofá-cama (cap 4 e 5) ───────────────────────────────────────────────────

def test_cap2_sem_sofa_cama():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "sofá-cama")

def test_cap3_sem_sofa_cama():
    linhas = itens_para_tipologia(3, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "sofá-cama")

def test_cap4_tem_sofa_cama():
    linhas = itens_para_tipologia(4, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "sofá-cama")

def test_cap5_tem_sofa_cama():
    linhas = itens_para_tipologia(5, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "sofá-cama")


# ── Área externa ─────────────────────────────────────────────────────────────

def test_sem_terraco_nao_tem_jacuzzi():
    linhas = itens_para_tipologia(4, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "jacuzzi")

def test_garden_tem_jacuzzi():
    linhas = itens_para_tipologia(4, "Garden", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "jacuzzi")

def test_terraco_tipo_tem_jacuzzi():
    linhas = itens_para_tipologia(4, "Terraço", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "jacuzzi")

def test_garden_nao_tem_mesa_externa():
    linhas = itens_para_tipologia(4, "Garden", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "mesa externa")

def test_sacada_tem_mesa_externa():
    linhas = itens_para_tipologia(5, "Sacada", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "mesa externa")

def test_varanda_tem_mesa_externa():
    linhas = itens_para_tipologia(3, "Varanda", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "mesa externa")

def test_sacada_nao_tem_jacuzzi():
    linhas = itens_para_tipologia(5, "Sacada", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "jacuzzi")


# ── PCD ──────────────────────────────────────────────────────────────────────

def test_pcd_marca_banheiro_como_pcd():
    linhas = itens_para_tipologia(2, "Sem", "PCD", PRODUTOS_VAZIO)
    assert any("PCD" in l.item for l in linhas)


# ── Cadeiras ─────────────────────────────────────────────────────────────────

def test_cadeiras_cap2_qty2():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 2

def test_cadeiras_cap3_qty3():
    linhas = itens_para_tipologia(3, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 3

def test_cadeiras_cap4_qty3():
    linhas = itens_para_tipologia(4, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 3

def test_cadeiras_cap5_qty4():
    linhas = itens_para_tipologia(5, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 4


# ── Catálogo sobrescreve preço ────────────────────────────────────────────────

def test_catalogo_sobrescreve_preco_default():
    produtos = {"MRC0002": Produto("MRC0002", "Gabinete inferior", "MARCENARIA", 9999.0)}
    linhas = itens_para_tipologia(2, "Sem", "Padrão", produtos)
    gab = next(l for l in linhas if "gabinete inferior" in l.item.lower())
    assert gab.valor_unitario == 9999.0


# ── Cálculos ─────────────────────────────────────────────────────────────────

def test_subtotais_batem_com_soma_das_linhas():
    linhas = itens_para_tipologia(4, "Garden", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Garden · Padrão · Cap. 4", "Clean", "Natal Spot", linhas)
    for cat, subtotal in m.subtotais.items():
        esperado = round(sum(l.valor_total for l in m.linhas if l.categoria == cat), 2)
        assert subtotal == esperado, f"Subtotal {cat}: {subtotal} != {esperado}"

def test_taxa_adm_e_13_porcento():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.taxa_adm == round(m.valor_produtos * 0.13, 2)

def test_total_geral_soma_correta():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.total_geral == round(m.valor_produtos + m.taxa_decor + m.taxa_adm, 2)

def test_taxa_decor_fixo_2500():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.taxa_decor == 2500.0

def test_cap5_garden_total_maior_que_cap2_sem():
    l2 = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    l5 = itens_para_tipologia(5, "Garden", "Padrão", PRODUTOS_VAZIO)
    m2 = montar_memorial("A", "", "Clean", "X", l2)
    m5 = montar_memorial("B", "", "Clean", "X", l5)
    assert m5.total_geral > m2.total_geral


# ── CSV ───────────────────────────────────────────────────────────────────────

def test_csv_contem_cabecalho_item():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "ITEM" in csv_text

def test_csv_contem_total_geral():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "TOTAL GERAL" in csv_text

def test_csv_contem_taxa_decor():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "Taxa Decor" in csv_text

def test_csv_contem_nome_spot():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "Natal Spot" in csv_text
