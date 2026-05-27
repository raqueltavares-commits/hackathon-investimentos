import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from acabamentos import acabamento_de, META_ITEM


def test_biofilico_gabinete_inferior():
    assert acabamento_de("biofilico", "gabinete_inferior") == "Mdf areia"

def test_biofilico_bancada_pedra():
    assert acabamento_de("biofilico", "bancada_coz_pedra") == "Granito pitaya"

def test_fallback_a_confirmar_para_role_desconhecido():
    assert acabamento_de("biofilico", "role_inexistente") == "A confirmar"

def test_estilo_desconhecido_cai_em_a_confirmar():
    assert acabamento_de("inexistente", "gabinete_inferior") == "A confirmar"

def test_todos_estilos_existem():
    for e in ("clean", "biofilico", "industrial", "bruma"):
        assert acabamento_de(e, "cama_queen")  # string não vazia

def test_meta_item_tem_ambiente():
    assert META_ITEM["gabinete_inferior"]["ambiente"] == "Cozinha"
    assert META_ITEM["cabeceira"]["ambiente"] == "Quarto"
    assert META_ITEM["box_banheiro"]["ambiente"] == "Banheiro"
