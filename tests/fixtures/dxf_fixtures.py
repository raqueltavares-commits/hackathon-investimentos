"""Fixtures de DXF gerados na memória para testar parsing sem arquivo real.

Reflete a estrutura do export Revit real (validada no Bonito):
- numeros de unidade em A-AREA-IDEN (TEXT)
- esquadrias como blocos INSERT no layer A-GLAZ
- nearest-label associa cada bloco à unidade mais próxima

Cada janela = 2 blocos A-GLAZ (caixilho + folha), pra exercitar a normalizacao
(blocos crus -> nº de janelas). Unidade de esquina tem 2 janelas (4 blocos).
"""

import io

import ezdxf

BLOCOS_POR_JANELA = 2


def _add_janela(msp, blk_name, x, y):
    """Insere os blocos de uma janela (2 INSERTs no layer A-GLAZ)."""
    for i in range(BLOCOS_POR_JANELA):
        msp.add_blockref(
            blk_name,
            insert=(x + i * 0.1, y),
            dxfattribs={"layer": "A-GLAZ"},
        )


def criar_dxf_teste() -> bytes:
    """DXF com 3 unidades (101, 102, 103); 103 é de esquina (2 janelas vs 1).

    Esperado (janelas normalizadas): 101->1, 102->1, 103->2.
    """
    doc = ezdxf.new("R2018")
    blk = doc.blocks.new(name="JANELA")
    blk.add_line((0, 0), (1, 0))  # geometria minima do bloco
    msp = doc.modelspace()

    # Unidade 101: numero em (5,5), 1 janela na fachada (y=10)
    msp.add_text("101", dxfattribs={"layer": "A-AREA-IDEN", "insert": (5, 5)})
    _add_janela(msp, "JANELA", 5, 10)

    # Unidade 102: numero em (15,5), 1 janela
    msp.add_text("102", dxfattribs={"layer": "A-AREA-IDEN", "insert": (15, 5)})
    _add_janela(msp, "JANELA", 15, 10)

    # Unidade 103 (esquina): numero em (25,5), 2 janelas (fachada + lateral)
    msp.add_text("103", dxfattribs={"layer": "A-AREA-IDEN", "insert": (25, 5)})
    _add_janela(msp, "JANELA", 25, 10)
    _add_janela(msp, "JANELA", 30, 5)

    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue()


def carregar_msp(dxf_bytes: str):
    """Le os bytes DXF e devolve o modelspace ezdxf."""
    from io import StringIO

    doc = ezdxf.read(StringIO(dxf_bytes))
    return doc.modelspace()
