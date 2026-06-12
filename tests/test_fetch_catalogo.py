import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "skills/orcamento-decor/scripts"
REFS = Path(__file__).parent.parent / "skills/orcamento-decor/references"
sys.path.insert(0, str(SCRIPTS))

from montar_orcamento import _ITENS_PLUS


def test_depara_cobre_todos_os_itens_plus():
    depara = json.loads((REFS / "depara-catalogo.json").read_text(encoding="utf-8"))
    codigos_itens = {codigo for (_role, _cat, codigo, _desc, _val) in _ITENS_PLUS}
    assert codigos_itens.issubset(depara.keys()), (
        f"Faltam no de-para: {codigos_itens - depara.keys()}"
    )


def test_depara_aponta_para_codigos_inteiros():
    depara = json.loads((REFS / "depara-catalogo.json").read_text(encoding="utf-8"))
    assert all(isinstance(v, int) for v in depara.values())
