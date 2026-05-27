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
            with poly_ent.points() as pts_ctx:
                pts = list(pts_ctx)
        except Exception:
            continue
        if len(pts) < 3:
            continue
        # Normaliza para (x, y) tuple -- suporta numpy array ou lista de tuples
        try:
            pts_list = [(float(p[0]), float(p[1])) for p in pts]
        except Exception:
            continue
        # Centro do poligono para encontrar texto mais proximo
        cx = sum(p[0] for p in pts_list) / len(pts_list)
        cy = sum(p[1] for p in pts_list) / len(pts_list)

        nome = _encontrar_texto_proximo(textos, cx, cy)
        if nome:
            poligonos[nome] = pts_list

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
    """Extrai inserts de janela (A-GLAZ-IDEN) com marca e posicao.

    Aceita tanto INSERT (blocos com atributo MARK) quanto TEXT
    (ODA costuma exportar blocos como texto simples).
    """
    janelas = []
    for e in msp:
        if e.dxf.layer != "A-GLAZ-IDEN":
            continue
        dxftype = e.dxftype()
        if dxftype == "INSERT":
            marca = ""
            if hasattr(e, "get_attrib_text"):
                marca = e.get_attrib_text("MARK") or e.get_attrib_text("TAG") or ""
            pt = e.dxf.insert
            janelas.append((marca, (pt.x, pt.y)))
        elif dxftype == "TEXT":
            # ODA often converts block inserts to TEXT in DXF output
            try:
                texto = e.dxf.text or ""
            except Exception:
                texto = ""
            try:
                pt = e.dxf.insert
                janelas.append((texto.strip(), (pt.x, pt.y)))
            except Exception:
                continue
    return janelas


def _associar_janelas_a_unidades(janelas, poligonos):
    """Point-in-polygon: para cada janela, identifica a unidade que a contem.

    Usa covers() em vez de contains() para tambem capturar pontos exatamente
    no contorno do poligono (esquadrias em paredes externas podem ter
    coordenadas na borda do poligono de area).
    """
    from shapely.geometry import Point, Polygon

    unidade_janelas = {u: [] for u in poligonos}
    poly_cache = {nome: Polygon(pts) for nome, pts in poligonos.items()}

    for marca, (x, y) in janelas:
        pt = Point(x, y)
        for nome, poly in poly_cache.items():
            if poly.covers(pt):  # covers = contains + boundary
                unidade_janelas[nome].append((marca, (x, y)))
                break
    return unidade_janelas
