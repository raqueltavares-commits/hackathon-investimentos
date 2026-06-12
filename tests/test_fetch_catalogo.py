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


FIXTURES = Path(__file__).parent / "fixtures"


def test_parsear_resposta_mapeia_codigo_item_para_preco():
    from fetch_catalogo import parsear_resposta
    texto = (FIXTURES / "produto_api_sample.json").read_text(encoding="utf-8")
    depara = {"MRC0002": 73, "MOB0001": 190, "MOB0003": 333, "ELE0006": 449}
    produtos = parsear_resposta(texto, depara)
    assert produtos["MRC0002"]["valor_unitario"] == 2700.0
    assert produtos["ELE0006"]["valor_unitario"] == 1319.0


def test_parsear_resposta_normaliza_nome():
    from fetch_catalogo import parsear_resposta
    texto = (FIXTURES / "produto_api_sample.json").read_text(encoding="utf-8")
    depara = {"MOB0003": 333}
    produtos = parsear_resposta(texto, depara)
    assert produtos["MOB0003"]["nome"] == "Sofá-cama | Belize Aveia"


def test_parsear_resposta_ignora_codigo_fora_do_depara():
    from fetch_catalogo import parsear_resposta
    texto = '[{"codigo": 999, "nome": "X", "valor": 10.0, "subcategoria_codigo": "2.1.1"}]'
    produtos = parsear_resposta(texto, {"MRC0002": 73})
    assert produtos == {}


def test_carregar_depara_le_arquivo_padrao():
    from fetch_catalogo import carregar_depara
    depara = carregar_depara(None)
    assert depara["MRC0002"] == 73


def test_buscar_catalogo_orquestra_com_http_fake():
    from fetch_catalogo import buscar_catalogo

    def http_fake(url, headers=None):
        if url.endswith("seazone-decor-interno.seazone.properties/"):
            return '<script src="/assets/index-ABC123.js"></script>'
        if url.endswith("assets/index-ABC123.js"):
            return 'x="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.sig-_12345678";'
        if "/rest/v1/produto" in url:
            assert headers and headers.get("apikey", "").startswith("eyJ")
            return '[{"codigo": 73, "nome": "Gabinete inferior", "valor": 2700.0, "subcategoria_codigo": "2.1.1"}]'
        raise AssertionError(f"URL inesperada: {url}")

    produtos = buscar_catalogo({"MRC0002": 73}, http_get=http_fake)
    assert produtos["MRC0002"]["valor_unitario"] == 2700.0


def test_buscar_catalogo_sem_bundle_levanta_erro():
    from fetch_catalogo import buscar_catalogo, CatalogoError

    def http_fake(url, headers=None):
        return "<html>sem bundle</html>"

    import pytest
    with pytest.raises(CatalogoError):
        buscar_catalogo({"MRC0002": 73}, http_get=http_fake)


def test_buscar_catalogo_bundle_sem_jwt_levanta_erro():
    from fetch_catalogo import buscar_catalogo, CatalogoError

    def http_fake(url, headers=None):
        if url.endswith("assets/index-ABC123.js"):
            return "const x = 'sem token jwt aqui';"
        return '<script src="/assets/index-ABC123.js"></script>'

    import pytest
    with pytest.raises(CatalogoError, match="[Aa]non key"):
        buscar_catalogo({"MRC0002": 73}, http_get=http_fake)


def test_extrai_anon_key_prefere_role_anon_sobre_service_role():
    from fetch_catalogo import extrair_anon_key
    # service_role primeiro (payload {"role":"service_role"}), anon depois.
    service = "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.sig-_service01"
    anon = "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.sig-_anon012345"
    js = f'a="{service}";b="{anon}";'
    assert extrair_anon_key(js) == anon


def test_extrai_bundle_path_prefere_index_sobre_vendor():
    from fetch_catalogo import extrair_bundle_path
    html = ('<script src="/assets/vendor-XYZ.js"></script>'
            '<script src="/assets/index-ABC123.js"></script>')
    assert extrair_bundle_path(html) == "assets/index-ABC123.js"
