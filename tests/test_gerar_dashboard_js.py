import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from gerar_dashboard_js import (
    parsear_js, serializar_js, construir_entrada, upsert_spot,
)

MEMORIAIS = {
    "memoriais": [
        {"tipologia": "A", "descricao": "Sem · Padrão · Cap. 2", "total_geral": 41766.0},
        {"tipologia": "B", "descricao": "Garden · Padrão · Cap. 4", "total_geral": 53079.0},
    ]
}
MEMORIAL_URLS = {"A": "https://drive/A", "B": "https://drive/B"}


def test_parsear_js_vazio_quando_string_vazia():
    assert parsear_js("") == {"index": [], "spots": {}}


def test_parsear_js_le_window_orcamentos():
    texto = 'window.ORCAMENTOS = {"index": [], "spots": {"x": 1}};\n'
    assert parsear_js(texto) == {"index": [], "spots": {"x": 1}}


def test_serializar_js_roundtrip():
    dados = {"index": [{"slug": "natal-spot"}], "spots": {"natal-spot": {"spot": "Natal"}}}
    texto = serializar_js(dados)
    assert texto.startswith("//")
    assert "window.ORCAMENTOS =" in texto
    assert parsear_js(texto) == dados


def test_construir_entrada_index_tem_campos():
    idx, _ = construir_entrada(
        spot="Natal Spot", codigo="6953", slug="natal-spot", estilo="Clean",
        consolidado_url="https://drive/cons", memoriais=MEMORIAIS,
        memorial_urls=MEMORIAL_URLS, gerado_em="2026-05-27")
    assert idx["spot"] == "Natal Spot"
    assert idx["slug"] == "natal-spot"
    assert idx["estilo"] == "Clean"
    assert idx["pacote"] == "Plus"
    assert idx["total_tipologias"] == 2
    assert idx["consolidado_url"] == "https://drive/cons"


def test_construir_entrada_spot_tem_tipologias_com_custo_e_url():
    _, sp = construir_entrada(
        spot="Natal Spot", codigo="6953", slug="natal-spot", estilo="Clean",
        consolidado_url="https://drive/cons", memoriais=MEMORIAIS,
        memorial_urls=MEMORIAL_URLS, gerado_em="2026-05-27")
    a = next(t for t in sp["tipologias"] if t["tipologia"] == "A")
    assert a["descricao"] == "Sem · Padrão · Cap. 2"
    assert a["custo"] == 41766.0
    assert a["memorial_url"] == "https://drive/A"


def test_construir_entrada_url_ausente_vira_hash():
    _, sp = construir_entrada(
        spot="X", codigo="1", slug="x", estilo="Clean",
        consolidado_url="https://drive/cons", memoriais=MEMORIAIS,
        memorial_urls={"A": "https://drive/A"}, gerado_em="2026-05-27")
    b = next(t for t in sp["tipologias"] if t["tipologia"] == "B")
    assert b["memorial_url"] == "#"


def test_upsert_adiciona_novo_spot():
    base = {"index": [], "spots": {}}
    idx = {"slug": "natal-spot", "spot": "Natal Spot"}
    sp = {"spot": "Natal Spot", "tipologias": []}
    res = upsert_spot(base, "natal-spot", idx, sp)
    assert len(res["index"]) == 1
    assert res["spots"]["natal-spot"] == sp


def test_upsert_substitui_spot_existente_sem_duplicar():
    base = {
        "index": [{"slug": "natal-spot", "spot": "Velho"}],
        "spots": {"natal-spot": {"spot": "Velho"}},
    }
    idx = {"slug": "natal-spot", "spot": "Novo"}
    sp = {"spot": "Novo", "tipologias": []}
    res = upsert_spot(base, "natal-spot", idx, sp)
    assert len(res["index"]) == 1
    assert res["index"][0]["spot"] == "Novo"
    assert res["spots"]["natal-spot"]["spot"] == "Novo"
