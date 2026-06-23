import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from montar_orcamento import itens_para_tipologia, montar_memorial, serializar_estruturado
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
    assert "METAIS E INOX" in cats


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


def test_catalogo_preenche_cor_e_referencia_link():
    produtos = {"MRC0002": Produto("MRC0002", "Gabinete", "MARCENARIA", 100.0,
                                   cor_acabamento="Freijó", link="https://x.com/73")}
    linhas = itens_para_tipologia(2, "Sem", "Padrão", produtos)
    gab = next(l for l in linhas if "gabinete inferior" in l.item.lower())
    assert gab.cor_acabamento == "Freijó"
    assert gab.referencia == "https://x.com/73"


def test_servico_puxa_preco_do_catalogo():
    # SRV0007 = Instalação de ar condicionado
    produtos = {"SRV0007": Produto("SRV0007", "Instalação ar", "SERVIÇOS", 815.0)}
    linhas = itens_para_tipologia(2, "Sem", "Padrão", produtos)
    ar = next(l for l in linhas if l.categoria == "SERVIÇOS" and "ar condicionado" in l.item.lower())
    assert ar.valor_unitario == 815.0


# ── Frete / Total + Frete ─────────────────────────────────────────────────────

def test_total_linha_soma_frete():
    from modelos import LinhaMemorial
    l = LinhaMemorial(categoria="MOBILIÁRIO", item="Sofá", quantidade=2,
                      valor_unitario=1000.0, frete=150.0)
    assert l.valor_total == 2000.0
    assert l.total_linha == 2150.0

def test_frete_default_zero_total_linha_igual_valor_total():
    from modelos import LinhaMemorial
    l = LinhaMemorial(categoria="X", item="Y", quantidade=1, valor_unitario=500.0)
    assert l.total_linha == l.valor_total == 500.0

def test_valor_produtos_inclui_frete():
    from modelos import LinhaMemorial
    linhas = [LinhaMemorial(categoria="A", item="i", quantidade=1, valor_unitario=100.0, frete=20.0)]
    m = montar_memorial("A", "x", "Clean", "X", linhas)
    assert m.valor_produtos == 120.0


# ── Cálculos ─────────────────────────────────────────────────────────────────

def test_subtotais_batem_com_soma_das_linhas():
    linhas = itens_para_tipologia(4, "Garden", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Garden · Padrão · Cap. 4", "Clean", "Natal Spot", linhas)
    for cat, subtotal in m.subtotais.items():
        esperado = round(sum(l.valor_total for l in m.linhas if l.categoria == cat), 2)
        assert subtotal == esperado, f"Subtotal {cat}: {subtotal} != {esperado}"

def test_unidade_nao_tem_taxa_adm():
    # Unidades NÃO levam Taxa Adm (só área comum).
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.taxa_adm == 0.0

def test_area_comum_tem_taxa_adm_13():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "x", "Clean", "Natal Spot", linhas, incluir_adm=True)
    assert m.taxa_adm == round(m.valor_produtos * 0.13, 2)

def test_total_geral_soma_correta():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.total_geral == round(m.valor_produtos + m.taxa_decor + m.taxa_adm, 2)

def test_taxa_decor_6_porcento():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.taxa_decor == round(m.valor_produtos * 0.06, 2)

def test_sem_decor_zera_taxa_decor():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "x", "Clean", "Natal Spot", linhas, tem_decor=False)
    assert m.taxa_decor == 0.0

def test_cap5_garden_total_maior_que_cap2_sem():
    l2 = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    l5 = itens_para_tipologia(5, "Garden", "Padrão", PRODUTOS_VAZIO)
    m2 = montar_memorial("A", "", "Clean", "X", l2)
    m5 = montar_memorial("B", "", "Clean", "X", l5)
    assert m5.total_geral > m2.total_geral


# ── Serializador estruturado ──────────────────────────────────────────────────

def test_estruturado_contem_total_geral():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    flat = [c for r in serializar_estruturado(m, "clean") for c in r]
    assert any("TOTAL GERAL" in str(c) for c in flat)

def test_estruturado_contem_nome_spot():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    flat = [c for r in serializar_estruturado(m, "clean") for c in r]
    assert any("Natal Spot" in str(c) for c in flat)
