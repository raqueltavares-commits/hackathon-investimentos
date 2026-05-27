"""Le DWG/DXF via ezdxf+ODA e conta esquadrias por unidade pra AGRUPAR tipologias.

Abordagem (validada no DWG real do Bonito, export Revit):
- O export Revit traz a planta de areas com os NUMEROS de unidade (layer A-AREA-IDEN)
  e os blocos de esquadria (layer A-GLAZ) na mesma regiao. Os limites de area
  (A-AREA-BNDY) vem como segmentos LINE soltos (nao polilinhas), entao point-in-polygon
  nao funciona — usamos NEAREST-LABEL.
- Cada esquadria vira o bloco A-GLAZ mais proximo de um numero de unidade.
- A contagem CRUA de blocos por unidade e normalizada (dividida pela contagem-base do
  piso, = nº de blocos por janela) pra estimar o nº de JANELAS por unidade.
- O objetivo NAO e montar tabela de esquadrias, e diferenciar o DESENHO: unidades com
  mesma area que diferem pela janela de esquina caem em contagens diferentes.

Limitacao conhecida: no TERREO as unidades costumam abrir por porta de correr (nao janela),
entao a contagem de janela ~0 e o agrupamento sai da AREA (PDF), nao do DWG.
"""

import re
from collections import Counter
from dataclasses import dataclass, field

ODA_PATH = r"C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe"

# Numero de unidade: 3 digitos, opcionalmente pareado (ex.: "201" ou "201-301").
UNIT_PAT = re.compile(r"^\d{3}(?:-\d{3})?$")
# Layers de esquadria (blocos de janela). A-GLAZ = janela; -IDEN = tag de tipo.
JANELA_LAYERS = ("A-GLAZ", "A-GLAZ-IDEN")
# Margem (em unidades do DWG) ao redor da regiao dos numeros, pra capturar as
# esquadrias na fachada e excluir outras plantas/legendas distantes do desenho.
MARGEM = 10.0


@dataclass
class ExtraidosDWG:
    contagem_blocos: dict[str, int]  # label de unidade -> nº cru de blocos A-GLAZ
    labels: list = field(default_factory=list)  # [(nome, x, y)]

    def janelas_por_unidade(self) -> dict[str, int]:
        """Normaliza a contagem crua de blocos em nº estimado de janelas.

        Divide pela contagem-base (o nº de blocos por janela do piso, = a contagem
        mais comum entre unidades). Limpa ruido do nearest-label (ex.: uma unidade
        pegando um bloco a mais da vizinha).
        """
        positivos = [c for c in self.contagem_blocos.values() if c > 0]
        if not positivos:
            return {n: 0 for n in self.contagem_blocos}
        base = Counter(positivos).most_common(1)[0][0]
        return {n: round(c / base) for n, c in self.contagem_blocos.items()}

    def contagem_por_unidade(self) -> dict[str, int]:
        """Contrato usado pelo agrupamento: janelas (normalizadas) por unidade."""
        return self.janelas_por_unidade()


def ler_dwg(caminho: str) -> ExtraidosDWG:
    """Le DWG (converte via ODA) e extrai a contagem de esquadrias por unidade."""
    import ezdxf
    from ezdxf.addons import odafc

    ezdxf.options.set("odafc-addon", "win_exec_path", ODA_PATH)
    doc = odafc.readfile(caminho)
    return extrair(doc.modelspace())


def extrair(msp) -> ExtraidosDWG:
    """Logica pura sobre um modelspace ezdxf (testavel sem ODA)."""
    labels = _coletar_labels_unidade(msp)
    janelas = _coletar_janelas(msp, labels)
    contagem = _contar_por_unidade(janelas, labels)
    return ExtraidosDWG(contagem_blocos=contagem, labels=labels)


def _coletar_labels_unidade(msp):
    """Numeros de unidade em A-AREA-IDEN (TEXT/MTEXT casando UNIT_PAT)."""
    labels = []
    for e in msp:
        if e.dxf.layer != "A-AREA-IDEN":
            continue
        if e.dxftype() not in ("TEXT", "MTEXT"):
            continue
        try:
            texto = e.dxf.text.strip()
        except Exception:
            continue
        # MTEXT pode ter quebras/formatacao; pega a 1a linha.
        texto = texto.splitlines()[0].strip() if texto else ""
        if UNIT_PAT.match(texto):
            try:
                p = e.dxf.insert
                labels.append((texto, float(p.x), float(p.y)))
            except Exception:
                continue
    return labels


def _regiao_labels(labels, margem=MARGEM):
    xs = [l[1] for l in labels]
    ys = [l[2] for l in labels]
    return (min(xs) - margem, max(xs) + margem, min(ys) - margem, max(ys) + margem)


def _coletar_janelas(msp, labels):
    """Blocos de esquadria (INSERT em A-GLAZ*) dentro da regiao dos numeros.

    A restricao de regiao evita capturar uma 2a planta (ex.: planta arquitetonica
    longe da planta de areas no mesmo arquivo), que jogaria todas as esquadrias na
    unidade da borda.
    """
    if not labels:
        return []
    x0, x1, y0, y1 = _regiao_labels(labels)
    janelas = []
    for e in msp:
        if e.dxf.layer not in JANELA_LAYERS:
            continue
        if e.dxftype() != "INSERT":
            continue
        try:
            p = e.dxf.insert
        except Exception:
            continue
        if x0 <= p.x <= x1 and y0 <= p.y <= y1:
            janelas.append((float(p.x), float(p.y)))
    return janelas


def _contar_por_unidade(janelas, labels):
    """Nearest-label: cada esquadria conta pra unidade cujo numero esta mais perto."""
    contagem = {nome: 0 for nome, _, _ in labels}
    for x, y in janelas:
        nome = _nearest(x, y, labels)
        if nome is not None:
            contagem[nome] += 1
    return contagem


def _nearest(x, y, labels):
    melhor = None
    melhor_dist = float("inf")
    for nome, lx, ly in labels:
        d = (lx - x) ** 2 + (ly - y) ** 2
        if d < melhor_dist:
            melhor_dist = d
            melhor = nome
    return melhor
