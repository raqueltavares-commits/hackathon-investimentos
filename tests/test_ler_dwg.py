"""Testes de integração com DXF gerado na memória (sem arquivo real)."""

import sys
from io import BytesIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tabela-tipologias" / "scripts"))

from ler_dwg import (
    ExtraidosDWG,
    _coletar_poligonos,
    _coletar_janelas,
    _associar_janelas_a_unidades,
)
from tests.fixtures.dxf_fixtures import criar_dxf_teste


def test_ler_dxf_gerado_na_memoria():
    """Testa parsing com DXF gerado na memória (2+2+3 esquadrias = 3 unidades)."""
    import ezdxf

    from io import StringIO

    dxf_bytes = criar_dxf_teste()
    # Simular leitura via ezdxf diretamente (sem ODA)
    doc = ezdxf.read(StringIO(dxf_bytes))
    msp = doc.modelspace()

    # Coletar polígonos e textos manualmente (testar a lógica)
    poligonos = _coletar_poligonos(msp)
    janelas = _coletar_janelas(msp)
    unidades = _associar_janelas_a_unidades(janelas, poligonos)

    extraidos = ExtraidosDWG(unidades=unidades, poligonos=poligonos)
    contagem = extraidos.contagem_por_unidade()

    # 101:2, 102:2, 103:3
    assert contagem.get("101", 0) == 2, f"101 esperava 2, got {contagem.get('101', 0)}"
    assert contagem.get("102", 0) == 2, f"102 esperava 2, got {contagem.get('102', 0)}"
    assert contagem.get("103", 0) == 3, f"103 esperava 3, got {contagem.get('103', 0)}"


def test_agrupar_com_esquadrias_separa_unidade_de_esquina():
    """Valida lógica: unidades com contagem diferente de esquadrias = tipologias separadas."""
    from montar_tabela import agrupar

    unidades = [
        {"unidade": "101", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 15.0, "area_unidade": 19.0},
        {"unidade": "102", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 15.2, "area_unidade": 19.3},
        {"unidade": "103", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 15.5, "area_unidade": 19.8},  # mesma área, mais esquadrias
    ]
    # Simular contagem do DXF: 101:2, 102:2, 103:3
    esquadrias = {"101": 2, "102": 2, "103": 3}

    tipologias, avisos = agrupar(unidades, esquadrias_por_unidade=esquadrias)

    # 103 tem 3 esquadrias (esquina) → tipologia separada
    assert len(tipologias) == 2, f"Esperado 2 tipologias, got {len(tipologias)}"

    # Verificar que 103 ficou separado
    tipos = [t for t in tipologias if "103" in t.get("unidades", [])]
    assert len(tipos) == 1, "103 deve estar em sua própria tipologia"
    assert tipos[0]["quantidade"] == 1


def test_pip_pack_ignora_textos_fora_de_poligonos():
    """Textos fora de qualquer polígono são ignorados (não causam erro)."""
    import ezdxf

    # DXF com texto no layer A-GLAZ-IDEN mas sem polígono associado
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()

    msp.add_lwpolyline(
        [(0, 0), (10, 0), (10, 10), (0, 10)],
        close=True,
        dxfattribs={"layer": "A-AREA-BNDY"},
    )
    msp.add_text("101", dxfattribs={"layer": "A-AREA-IDEN", "insert": (5, 5)})
    # Janela dentro do polígono
    msp.add_text("V1", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (5, 5)})
    # Janela FORA de qualquer polígono
    msp.add_text("V2", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (1000, 1000)})

    poligonos = _coletar_poligonos(msp)
    janelas = _coletar_janelas(msp)
    unidades = _associar_janelas_a_unidades(janelas, poligonos)

    extraidos = ExtraidosDWG(unidades=unidades, poligonos=poligonos)
    contagem = extraidos.contagem_por_unidade()

    # Apenas V1 foi associada a 101 (dentro do polígono)
    assert contagem.get("101", 0) == 1
    # V2 não foi associada a nenhuma unidade
    assert all(len(v) == 1 for u, v in unidades.items())


def test_contagem_vazia_quando_sem_janelas():
    """Sem janelas no DXF, todas as unidades ficam com contagem 0."""
    import ezdxf

    doc = ezdxf.new("R2018")
    msp = doc.modelspace()

    msp.add_lwpolyline(
        [(0, 0), (10, 0), (10, 10), (0, 10)],
        close=True,
        dxfattribs={"layer": "A-AREA-BNDY"},
    )
    msp.add_text("101", dxfattribs={"layer": "A-AREA-IDEN", "insert": (5, 5)})
    # Sem layer A-GLAZ-IDEN

    poligonos = _coletar_poligonos(msp)
    janelas = _coletar_janelas(msp)
    unidades = _associar_janelas_a_unidades(janelas, poligonos)

    extraidos = ExtraidosDWG(unidades=unidades, poligonos=poligonos)
    contagem = extraidos.contagem_por_unidade()

    assert contagem.get("101", 0) == 0