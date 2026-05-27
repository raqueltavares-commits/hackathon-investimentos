"""Testes de ler_dwg com DXF gerado na memória (sem arquivo real nem ODA).

A logica pura vive em `extrair(msp)`; aqui montamos modelspaces ezdxf e checamos
a contagem/normalizacao de janelas por unidade via nearest-label.
"""

import sys
from pathlib import Path

import ezdxf

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tabela-tipologias" / "scripts"))

from ler_dwg import extrair, listar_layers
from tests.fixtures.dxf_fixtures import carregar_msp, criar_dxf_teste


def _msp_vazio():
    return ezdxf.new("R2018").modelspace()


def _add_unidade(msp, numero, x, y):
    msp.add_text(numero, dxfattribs={"layer": "A-AREA-IDEN", "insert": (x, y)})


def _add_bloco_janela(msp, x, y, layer="A-GLAZ"):
    doc = msp.doc
    if "JANELA" not in doc.blocks:
        doc.blocks.new(name="JANELA").add_line((0, 0), (1, 0))
    msp.add_blockref("JANELA", insert=(x, y), dxfattribs={"layer": layer})


def test_fixture_separa_unidade_de_esquina():
    """101->1, 102->1, 103->2 janelas (103 é esquina)."""
    msp = carregar_msp(criar_dxf_teste())
    janelas = extrair(msp).janelas_por_unidade()
    assert janelas == {"101": 1, "102": 1, "103": 2}


def test_normaliza_blocos_por_janela():
    """Cada janela = N blocos; normaliza pra nº de janelas pela contagem-base."""
    msp = _msp_vazio()
    _add_unidade(msp, "201", 0, 0)
    _add_unidade(msp, "202", 10, 0)
    # 201: 1 janela = 3 blocos; 202: 2 janelas = 6 blocos
    for i in range(3):
        _add_bloco_janela(msp, 0 + i * 0.1, 1)
    for i in range(6):
        _add_bloco_janela(msp, 10 + i * 0.1, 1)
    janelas = extrair(msp).janelas_por_unidade()
    assert janelas == {"201": 1, "202": 2}


def test_nearest_label_associa_a_unidade_mais_proxima():
    """Cada bloco conta pra unidade cujo numero esta mais perto."""
    msp = _msp_vazio()
    _add_unidade(msp, "301", 0, 0)
    _add_unidade(msp, "302", 100, 0)
    _add_bloco_janela(msp, 2, 1)    # perto de 301
    _add_bloco_janela(msp, 98, 1)   # perto de 302
    contagem = extrair(msp).contagem_blocos
    assert contagem == {"301": 1, "302": 1}


def test_ignora_blocos_fora_da_regiao_dos_numeros():
    """Bloco longe da regiao dos numeros (ex.: 2a planta no mesmo arquivo) é excluido."""
    msp = _msp_vazio()
    _add_unidade(msp, "401", 0, 0)
    _add_unidade(msp, "402", 10, 0)
    _add_bloco_janela(msp, 5, 1)        # dentro da regiao
    _add_bloco_janela(msp, 5000, 5000)  # muito fora -> ignorado
    contagem = extrair(msp).contagem_blocos
    assert sum(contagem.values()) == 1


def test_aceita_label_pareado():
    """Numero de unidade pareado (ex.: '201-301') é reconhecido."""
    msp = _msp_vazio()
    _add_unidade(msp, "201-301", 0, 0)
    _add_bloco_janela(msp, 1, 1)
    janelas = extrair(msp).janelas_por_unidade()
    assert janelas == {"201-301": 1}


def test_sem_janelas_conta_zero():
    """Sem blocos A-GLAZ, todas as unidades ficam com 0 (caso térreo por porta)."""
    msp = _msp_vazio()
    _add_unidade(msp, "101", 0, 0)
    _add_unidade(msp, "102", 10, 0)
    extr = extrair(msp)
    assert extr.contagem_blocos == {"101": 0, "102": 0}
    assert extr.janelas_por_unidade() == {"101": 0, "102": 0}


def test_sem_labels_retorna_vazio():
    """Sem numeros de unidade, nao ha o que contar."""
    msp = _msp_vazio()
    _add_bloco_janela(msp, 0, 0)
    extr = extrair(msp)
    assert extr.contagem_blocos == {}
    assert extr.janelas_por_unidade() == {}


def test_layers_customizados_por_projeto():
    """Os nomes de layer variam por projeto -> aceitar override."""
    msp = _msp_vazio()
    # Projeto que nomeia diferente: numeros em "UNID-NUM", janelas em "JANELAS"
    msp.add_text("501", dxfattribs={"layer": "UNID-NUM", "insert": (0, 0)})
    _add_bloco_janela(msp, 1, 1, layer="JANELAS")
    # Com os defaults (A-AREA-IDEN/A-GLAZ) nao acha nada
    assert extrair(msp).contagem_blocos == {}
    # Com os layers do projeto, acha
    extr = extrair(msp, label_layer="UNID-NUM", janela_layers=("JANELAS",))
    assert extr.contagem_blocos == {"501": 1}


def test_listar_layers():
    """listar_layers ajuda a inspecionar um DWG novo."""
    msp = _msp_vazio()
    _add_unidade(msp, "101", 0, 0)
    _add_bloco_janela(msp, 1, 1)
    layers = listar_layers(msp)
    assert layers.get("A-AREA-IDEN", 0) >= 1
    assert layers.get("A-GLAZ", 0) >= 1
