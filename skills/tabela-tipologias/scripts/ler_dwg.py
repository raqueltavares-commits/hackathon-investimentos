"""Le DWG/DXF via ezdxf+ODA, extrai esquadrias por unidade."""

from dataclasses import dataclass

ODA_PATH = r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe"


@dataclass
class ExtraidosDWG:
    unidades: dict[str, list[tuple[str, tuple[float, float]]]]
    poligonos: dict[str, list[tuple[float, float]]]

    def contagem_por_unidade(self) -> dict[str, int]:
        return {u: len(v) for u, v in self.unidades.items()}


def ler_dwg(caminho: str) -> ExtraidosDWG:
    """Le arquivo DWG, extrai esquadrias do layer A-GLAZ e associa a unidades via poligonos."""
    import ezdxf
    from ezdxf.addons import odafc

    ezdxf.options.set("odafc-addon", "win_exec_path", ODA_PATH)
    doc = odafc.readfile(caminho)
    msp = doc.modelspace()

    poligonos = _coletar_poligonos(msp)
    janelas = _coletar_janelas(msp)
    unidades = _associar_janelas_a_unidades(janelas, poligonos)

    return ExtraidosDWG(unidades=unidades, poligonos=poligonos)


def _coletar_poligonos(msp):
    """Extrai poligonos de area (A-AREA-BNDY) com seu rotulo de area (A-AREA-IDEN)."""
    poligonos = {}
    entidades_por_layer = {}
    for e in msp:
        layer = e.dxf.layer
        if layer not in entidades_por_layer:
            entidades_por_layer[layer] = []
        entidades_por_layer[layer].append(e)

    if "A-AREA-BNDY" not in entidades_por_layer:
        return {}

    poligonos_lista = entidades_por_layer["A-AREA-BNDY"]
    textos = entidades_por_layer.get("A-AREA-IDEN", [])

    for poly_ent in poligonos_lista:
        try:
            pts = list(poly_ent.decoded_coords())
        except Exception:
            continue
        if len(pts) < 3:
            continue
        # Centro do poligono para encontrar texto mais proximo
        cx = sum(p.x for p in pts) / len(pts)
        cy = sum(p.y for p in pts) / len(pts)

        nome = _encontrar_texto_proximo(textos, cx, cy)
        if nome:
            poligonos[nome] = [(p.x, p.y) for p in pts]

    return poligonos


def _encontrar_texto_proximo(textos, cx, cy, raio=5000):
    """Encontra o texto mais proximo dentro de um raio (em unidades do DWG)."""
    melhor = None
    melhor_dist = raio ** 2
    for t in textos:
        if not hasattr(t, "dxf"):
            continue
        try:
            texto = t.dxf.text
            x, y = t.dxf.insert.x, t.dxf.insert.y
        except Exception:
            continue
        dist = (x - cx) ** 2 + (y - cy) ** 2
        if dist < melhor_dist:
            melhor_dist = dist
            melhor = texto
    return melhor


def _coletar_janelas(msp):
    """Extrai inserts de janela (A-GLAZ-IDEN) com marca e posicao."""
    janelas = []
    for e in msp:
        if e.dxf.layer == "A-GLAZ-IDEN" and e.dxftype() == "INSERT":
            marca = ""
            if hasattr(e, "get_attrib_text"):
                marca = e.get_attrib_text("MARK") or e.get_attrib_text("TAG") or ""
            pt = e.dxf.insert
            janelas.append((marca, (pt.x, pt.y)))
    return janelas


def _associar_janelas_a_unidades(janelas, poligonos):
    """Point-in-polygon: para cada janela, identifica a unidade que a contem."""
    from shapely.geometry import Point, Polygon

    unidade_janelas = {u: [] for u in poligonos}
    poly_cache = {nome: Polygon(pts) for nome, pts in poligonos.items()}

    for marca, (x, y) in janelas:
        pt = Point(x, y)
        for nome, poly in poly_cache.items():
            if poly.contains(pt):
                unidade_janelas[nome].append((marca, (x, y)))
                break
    return unidade_janelas
