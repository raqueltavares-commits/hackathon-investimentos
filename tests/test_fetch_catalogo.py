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


def test_extrai_bundle_path_do_html():
    from fetch_catalogo import extrair_bundle_path
    html = '<html><script type="module" src="/assets/index-DcpALHpp.js"></script></html>'
    assert extrair_bundle_path(html) == "assets/index-DcpALHpp.js"


def test_extrai_bundle_path_retorna_none_sem_match():
    from fetch_catalogo import extrair_bundle_path
    assert extrair_bundle_path("<html></html>") is None


def test_extrai_anon_key_jwt():
    from fetch_catalogo import extrair_anon_key
    js = 'const k="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.abc-_DEF123";'
    assert extrair_anon_key(js) == "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.abc-_DEF123"


def test_extrai_anon_key_retorna_none_sem_match():
    from fetch_catalogo import extrair_anon_key
    assert extrair_anon_key("sem token aqui") is None


def test_normalizar_corrige_double_utf8():
    from fetch_catalogo import normalizar
    assert normalizar("SofÃ¡-cama") == "Sofá-cama"


def test_normalizar_deixa_texto_limpo_intacto():
    from fetch_catalogo import normalizar
    assert normalizar("Cooktop 2 Bocas") == "Cooktop 2 Bocas"
