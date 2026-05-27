"""Fixtures de DXF gerados na memória para testar parsing sem arquivo real."""

import io

import ezdxf


def criar_dxf_teste() -> bytes:
    """Cria DXF minimal com:
    - 3 unidades (101, 102, 103)
    - Polígonos de área (A-AREA-BNDY)
    - Textos de identificação (A-AREA-IDEN): "101", "102", "103"
    - Janelas (A-GLAZ-IDEN): 2 em 101/102, 3 em 103 (esquina)
    """
    doc = ezdxf.new("R2018")
    msp = doc.modelspace()

    # Unidade 101: polígono retangular, texto "101", 2 janelas
    msp.add_lwpolyline(
        [(0, 0), (10, 0), (10, 10), (0, 10)],
        close=True,
        dxfattribs={"layer": "A-AREA-BNDY"},
    )
    msp.add_text("101", dxfattribs={"layer": "A-AREA-IDEN", "insert": (5, 5)})
    msp.add_text("V1", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (2, 10)})
    msp.add_text("V2", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (7, 10)})

    # Unidade 102: polígono retangular, texto "102", 2 janelas
    msp.add_lwpolyline(
        [(10, 0), (20, 0), (20, 10), (10, 10)],
        close=True,
        dxfattribs={"layer": "A-AREA-BNDY"},
    )
    msp.add_text("102", dxfattribs={"layer": "A-AREA-IDEN", "insert": (15, 5)})
    msp.add_text("V3", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (12, 10)})
    msp.add_text("V4", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (17, 10)})

    # Unidade 103: polígono, texto "103", 3 janelas (esquina)
    msp.add_lwpolyline(
        [(20, 0), (30, 0), (30, 10), (20, 10)],
        close=True,
        dxfattribs={"layer": "A-AREA-BNDY"},
    )
    msp.add_text("103", dxfattribs={"layer": "A-AREA-IDEN", "insert": (25, 5)})
    msp.add_text("V5", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (22, 10)})
    msp.add_text("V6", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (28, 10)})
    msp.add_text("V7", dxfattribs={"layer": "A-GLAZ-IDEN", "insert": (30, 5)})  # janela de esquina

    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue()