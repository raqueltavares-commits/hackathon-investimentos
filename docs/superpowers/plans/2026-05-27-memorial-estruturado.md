# Memorial Descritivo Estruturado — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer a skill `orcamento-decor` gerar autonomamente o memorial descritivo na estrutura oficial da Raquel (11 colunas, 4 linhas/item, ambiente, acabamento por estilo, serviços como itens, totais sem/com jacuzzi).

**Architecture:** Enriquece o catálogo interno (`_ITENS_PLUS`) e o modelo `LinhaMemorial` com ambiente/fornecedor/referência/acabamento/ficha técnica + flag `opcional` (jacuzzi). Paleta de acabamentos por estilo num módulo de dados. Novo serializador que produz a matriz de 11 colunas e um builder `.xlsx` multi-aba. `total_geral` passa a ser o "sem jacuzzi".

**Tech Stack:** Python 3.12 stdlib + openpyxl, pytest.

---

## File Structure

```
skills/orcamento-decor/scripts/
  modelos.py            # MODIFICA: LinhaMemorial ganha campos; MemorialTipologia ganha totais sem/com jacuzzi
  acabamentos.py        # NOVO: paleta de acabamento por estilo + metadata de ambiente/fornecedor/ficha por item
  servicos.py           # NOVO: lista fixa de serviços (INSUMOS)
  montar_orcamento.py   # MODIFICA: itens enriquecidos + serviços + serializador estruturado + xlsx
  gerar_xlsx.py         # NOVO: monta .xlsx multi-aba a partir das matrizes
skills/orcamento-decor/references/
  acabamentos-por-estilo.md   # NOVO: doc da paleta
tests/
  test_acabamentos.py         # NOVO
  test_memorial_estruturado.py # NOVO (matriz 11 colunas, totais sem/com jacuzzi, serviços)
  test_montar_orcamento.py    # MODIFICA: ajusta aos novos campos/totais
```

---

## Task 1: modelos.py — enriquecer LinhaMemorial e totais sem/com jacuzzi

**Files:**
- Modify: `skills/orcamento-decor/scripts/modelos.py`
- Test: `tests/test_montar_orcamento.py` (ajuste posterior na Task 5)

- [ ] **Step 1: Reescrever `modelos.py`**

```python
"""Dataclasses compartilhados entre os scripts de orçamento."""
from dataclasses import dataclass, field


@dataclass
class Produto:
    codigo: str
    nome: str
    categoria: str
    valor_unitario: float
    unidade: str = "un"


@dataclass
class LinhaMemorial:
    categoria: str
    item: str
    quantidade: int
    valor_unitario: float
    ambiente: str = ""
    fornecedor: str = "Catálogo Decor"
    referencia: str = ""
    acabamento: str = "A confirmar"
    largura: str = "A confirmar"
    altura: str = "A confirmar"
    profundidade: str = "A confirmar"
    opcional: bool = False  # True = fora do total base (ex: jacuzzi)

    @property
    def valor_total(self) -> float:
        return round(self.quantidade * self.valor_unitario, 2)


@dataclass
class MemorialTipologia:
    tipologia: str
    descricao: str
    estilo: str
    spot: str
    linhas: list[LinhaMemorial] = field(default_factory=list)
    taxa_decor: float = 2500.0

    @property
    def valor_produtos(self) -> float:
        """Soma das linhas NÃO opcionais (base, sem jacuzzi)."""
        return round(sum(l.valor_total for l in self.linhas if not l.opcional), 2)

    @property
    def valor_opcionais(self) -> float:
        """Soma das linhas opcionais (ex: jacuzzi)."""
        return round(sum(l.valor_total for l in self.linhas if l.opcional), 2)

    @property
    def taxa_adm(self) -> float:
        return round(self.valor_produtos * 0.13, 2)

    @property
    def subtotais(self) -> dict[str, float]:
        """Subtotal por categoria, incluindo opcionais (espelha o modelo da Raquel)."""
        result: dict[str, float] = {}
        for l in self.linhas:
            result[l.categoria] = round(result.get(l.categoria, 0.0) + l.valor_total, 2)
        return result

    @property
    def total_geral(self) -> float:
        """Total SEM jacuzzi (headline) = produtos base + taxa decor + taxa adm."""
        return round(self.valor_produtos + self.taxa_decor + self.taxa_adm, 2)

    @property
    def total_com_jacuzzi(self) -> float:
        return round(self.total_geral + self.valor_opcionais, 2)
```

- [ ] **Step 2: Rodar a suite (vai quebrar testes antigos — esperado, ajustados na Task 5)**

Run: `python -m pytest tests/test_montar_orcamento.py -q`
Expected: alguns FAILs ligados a jacuzzi/total (serão corrigidos na Task 5). `modelos` importa sem erro.

- [ ] **Step 3: Commit**

```bash
git add skills/orcamento-decor/scripts/modelos.py
git commit -m "feat(memorial): LinhaMemorial enriquecida + totais sem/com jacuzzi"
```

---

## Task 2: acabamentos.py — paleta por estilo + metadata por item

**Files:**
- Create: `skills/orcamento-decor/scripts/acabamentos.py`
- Create: `tests/test_acabamentos.py`

- [ ] **Step 1: Escrever `tests/test_acabamentos.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from acabamentos import acabamento_de, META_ITEM


def test_biofilico_gabinete_inferior():
    assert acabamento_de("biofilico", "gabinete_inferior") == "Mdf areia"

def test_biofilico_bancada_pedra():
    assert acabamento_de("biofilico", "bancada_coz_pedra") == "Granito pitaya"

def test_fallback_a_confirmar_para_role_desconhecido():
    assert acabamento_de("biofilico", "role_inexistente") == "A confirmar"

def test_estilo_desconhecido_cai_em_a_confirmar():
    assert acabamento_de("inexistente", "gabinete_inferior") == "A confirmar"

def test_todos_estilos_existem():
    for e in ("clean", "biofilico", "industrial", "bruma"):
        assert acabamento_de(e, "cama_queen")  # string não vazia

def test_meta_item_tem_ambiente():
    assert META_ITEM["gabinete_inferior"]["ambiente"] == "Cozinha"
    assert META_ITEM["cabeceira"]["ambiente"] == "Quarto"
    assert META_ITEM["box_banheiro"]["ambiente"] == "Banheiro"
```

- [ ] **Step 2: Rodar pra confirmar falha**

Run: `python -m pytest tests/test_acabamentos.py -q`
Expected: `ModuleNotFoundError: No module named 'acabamentos'`

- [ ] **Step 3: Escrever `skills/orcamento-decor/scripts/acabamentos.py`**

```python
"""Metadata de itens (ambiente/fornecedor) + paleta de acabamento por estilo.

A paleta é EMBUTIDA e calibravel: Biofilico veio do memorial-exemplo da Raquel;
Clean/Industrial/Bruma sao paletas iniciais coerentes com o estilo. Fallback "A confirmar".
"""

# Ambiente e fornecedor por role (independe do estilo)
META_ITEM: dict[str, dict[str, str]] = {
    "gabinete_inferior":   {"ambiente": "Cozinha"},
    "gabinete_superior":   {"ambiente": "Cozinha"},
    "cabeceira":           {"ambiente": "Quarto"},
    "arara_roupas":        {"ambiente": "Quarto"},
    "bancada_refeicao":    {"ambiente": "Cozinha"},
    "movel_apoio":         {"ambiente": "Quarto"},
    "prateleira_banheiro": {"ambiente": "Banheiro"},
    "bancada_coz_pedra":   {"ambiente": "Cozinha"},
    "bancada_ban_pedra":   {"ambiente": "Banheiro"},
    "cama_queen":          {"ambiente": "Quarto"},
    "sofa_cama":           {"ambiente": "Quarto"},
    "puff":                {"ambiente": "Quarto"},
    "cadeira_jantar":      {"ambiente": "Cozinha"},
    "torneira_coz":        {"ambiente": "Cozinha"},
    "cuba_coz":            {"ambiente": "Cozinha"},
    "cuba_ban":            {"ambiente": "Banheiro"},
    "torneira_ban":        {"ambiente": "Banheiro"},
    "box_banheiro":        {"ambiente": "Banheiro"},
    "filtro_agua":         {"ambiente": "Cozinha"},
    "toalheiro_termico":   {"ambiente": "Banheiro"},
    "kit_metais":          {"ambiente": "Banheiro"},
    "cooktop":             {"ambiente": "Cozinha"},
    "frigobar":            {"ambiente": "Cozinha"},
    "microondas":          {"ambiente": "Cozinha"},
    "cafeteira":           {"ambiente": "Cozinha"},
    "chaleira":            {"ambiente": "Cozinha"},
    "liquidificador":      {"ambiente": "Cozinha"},
    "depurador":           {"ambiente": "Cozinha"},
    "mini_grill":          {"ambiente": "Cozinha"},
    "tv":                  {"ambiente": "Quarto"},
    "iluminacao":          {"ambiente": "Geral"},
    "jacuzzi":             {"ambiente": "Garden"},
    "mesa_externa":        {"ambiente": "Garden"},
}

# Acabamento por estilo -> role. Biofilico calibrado do exemplo.
_ACABAMENTO: dict[str, dict[str, str]] = {
    "biofilico": {
        "gabinete_inferior":   "Mdf areia",
        "gabinete_superior":   "Mdf sava e palhinha com metal bege claro",
        "cabeceira":           "Mdf savana",
        "arara_roupas":        "Mdf savana, areia, palhinha e metal bege claro",
        "bancada_refeicao":    "Mdf areia",
        "movel_apoio":         "Mdf areia",
        "prateleira_banheiro": "Mdf savana e metal bege claro",
        "bancada_coz_pedra":   "Granito pitaya",
        "bancada_ban_pedra":   "Granito pitaya",
        "cama_queen":          "Suede preto",
        "sofa_cama":           "Linho cru",
        "puff":                "Linho cru",
        "cadeira_jantar":      "Madeira clara com palhinha",
        "iluminacao":          "Led / bege",
    },
    "clean": {
        "gabinete_inferior":   "Mdf branco",
        "gabinete_superior":   "Mdf branco com metal cromado",
        "cabeceira":           "Mdf off-white",
        "arara_roupas":        "Mdf branco e metal cromado",
        "bancada_refeicao":    "Mdf branco",
        "movel_apoio":         "Mdf branco",
        "prateleira_banheiro": "Mdf branco",
        "bancada_coz_pedra":   "Granito branco",
        "bancada_ban_pedra":   "Granito branco",
        "cama_queen":          "Suede off-white",
        "sofa_cama":           "Linho cinza claro",
        "puff":                "Linho cinza claro",
        "cadeira_jantar":      "Madeira clara",
        "iluminacao":          "Led / branco",
    },
    "industrial": {
        "gabinete_inferior":   "Mdf grafite",
        "gabinete_superior":   "Mdf grafite com metal preto",
        "cabeceira":           "Mdf carvalho escuro",
        "arara_roupas":        "Metal preto",
        "bancada_refeicao":    "Mdf grafite",
        "movel_apoio":         "Mdf grafite",
        "prateleira_banheiro": "Metal preto",
        "bancada_coz_pedra":   "Granito preto",
        "bancada_ban_pedra":   "Granito preto",
        "cama_queen":          "Suede grafite",
        "sofa_cama":           "Couro caramelo",
        "puff":                "Couro caramelo",
        "cadeira_jantar":      "Metal preto com madeira escura",
        "iluminacao":          "Led / preto",
    },
    "bruma": {
        "gabinete_inferior":   "Mdf fendi",
        "gabinete_superior":   "Mdf fendi com metal champagne",
        "cabeceira":           "Mdf cinza claro",
        "arara_roupas":        "Mdf fendi e metal champagne",
        "bancada_refeicao":    "Mdf fendi",
        "movel_apoio":         "Mdf fendi",
        "prateleira_banheiro": "Mdf fendi",
        "bancada_coz_pedra":   "Granito cinza",
        "bancada_ban_pedra":   "Granito cinza",
        "cama_queen":          "Suede cinza",
        "sofa_cama":           "Linho areia",
        "puff":                "Linho areia",
        "cadeira_jantar":      "Madeira acinzentada",
        "iluminacao":          "Led / champagne",
    },
}

# Acabamentos de metais/eletros independem muito do estilo
_ACABAMENTO_FIXO: dict[str, str] = {
    "torneira_coz":      "Cromado",
    "cuba_coz":          "Inox acetinado",
    "cuba_ban":          "Branco",
    "torneira_ban":      "Cromado",
    "box_banheiro":      "Alumínio escovado",
    "filtro_agua":       "Branco",
    "toalheiro_termico": "Cromado",
    "kit_metais":        "Cromado",
    "cooktop":           "Preto",
    "frigobar":          "Preto",
    "microondas":        "Inox espelhado",
    "cafeteira":         "Inox/Preto",
    "chaleira":          "Inox/Preto",
    "liquidificador":    "Preto",
    "depurador":         "Inox",
    "mini_grill":        "Inox/Preto",
    "tv":                "Preto",
    "jacuzzi":           "N/A",
    "mesa_externa":      "Preto",
}


def acabamento_de(estilo: str, role: str) -> str:
    e = (estilo or "").strip().lower()
    if role in _ACABAMENTO_FIXO:
        return _ACABAMENTO_FIXO[role]
    return _ACABAMENTO.get(e, {}).get(role, "A confirmar")
```

- [ ] **Step 4: Rodar e confirmar que passa**

Run: `python -m pytest tests/test_acabamentos.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/orcamento-decor/scripts/acabamentos.py tests/test_acabamentos.py
git commit -m "feat(memorial): paleta de acabamento por estilo + metadata de ambiente"
```

---

## Task 3: servicos.py — categoria INSUMOS (serviços como itens)

**Files:**
- Create: `skills/orcamento-decor/scripts/servicos.py`
- Test: coberto em `tests/test_memorial_estruturado.py` (Task 4)

- [ ] **Step 1: Escrever `skills/orcamento-decor/scripts/servicos.py`**

```python
"""Serviços (categoria INSUMOS) com preços de referência. Entram como itens no memorial."""

# (role, nome, ambiente, codigo, valor_default)
SERVICOS = [
    ("inst_eletrica",   "Serviços de elétrica e iluminação", "Serviços", "SRV0005", 350.0),
    ("inst_hidraulica", "Serviços hidráulicos",              "Serviços", "SRV0006", 300.0),
    ("inst_ar",         "Instalação de ar-condicionado",     "Serviços", "SRV0007", 800.0),
    ("inst_geral",      "Insumos e instalações gerais",      "Serviços", "SRV0008", 250.0),
    ("pintura",         "Pintura lisa",                      "Serviços", "SRV0001", 560.0),
    ("feltro",          "Feltro em todos os mobiliários",    "Serviços", "SRV0003", 200.0),
    ("limpeza",         "Limpeza pesada",                    "Serviços", "SRV0010", 250.0),
]
```

- [ ] **Step 2: Commit**

```bash
git add skills/orcamento-decor/scripts/servicos.py
git commit -m "feat(memorial): serviços (INSUMOS) com preços de referência"
```

---

## Task 4: montar_orcamento.py — itens enriquecidos + serviços + serializador estruturado + testes

**Files:**
- Modify: `skills/orcamento-decor/scripts/montar_orcamento.py`
- Create: `tests/test_memorial_estruturado.py`

- [ ] **Step 1: Escrever `tests/test_memorial_estruturado.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from montar_orcamento import (
    itens_para_tipologia, montar_memorial, serializar_estruturado,
)

PV: dict = {}


def _linhas(cap, terraco, tipo="Padrão"):
    return itens_para_tipologia(cap, terraco, tipo, PV)


def test_itens_tem_ambiente_e_acabamento():
    linhas = _linhas(2, "Sem")
    gab = next(l for l in linhas if "gabinete inferior" in l.item.lower())
    assert gab.ambiente == "Cozinha"
    assert gab.acabamento  # não vazio


def test_acabamento_varia_por_estilo():
    # itens_para_tipologia recebe estilo agora
    bio = itens_para_tipologia(2, "Sem", "Padrão", PV, estilo="biofilico")
    cln = itens_para_tipologia(2, "Sem", "Padrão", PV, estilo="clean")
    gb = next(l for l in bio if "gabinete inferior" in l.item.lower())
    gc = next(l for l in cln if "gabinete inferior" in l.item.lower())
    assert gb.acabamento != gc.acabamento


def test_servicos_presentes():
    linhas = _linhas(2, "Sem")
    assert any(l.categoria == "INSUMOS" for l in linhas)
    assert any("pintura" in l.item.lower() for l in linhas)


def test_jacuzzi_opcional_em_garden():
    linhas = _linhas(4, "Garden")
    jac = next(l for l in linhas if "jacuzzi" in l.item.lower())
    assert jac.opcional is True


def test_jacuzzi_fora_do_total_base():
    g = montar_memorial("A", "Garden", "Biofílico", "X", _linhas(4, "Garden"))
    s = montar_memorial("B", "Sem", "Biofílico", "X", _linhas(4, "Sem"))
    # total base (sem jacuzzi) de garden == sem (mesmos itens base)
    assert g.total_geral == s.total_geral
    # com jacuzzi é maior
    assert g.total_com_jacuzzi > g.total_geral
    assert round(g.total_com_jacuzzi - g.total_geral, 2) == g.valor_opcionais


def test_serializar_estruturado_cabecalho_11_colunas():
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Biofílico", "Bonito Spot", _linhas(2, "Sem"))
    rows = serializar_estruturado(m, "biofilico")
    header = next(r for r in rows if "ITEM/TIPO" in r or "ITEM/ TIPO" in r or "AMBIENTE" in r)
    assert "AMBIENTE" in header
    assert "FICHA TÉCNICA" in header
    assert "VALOR UNITÁRIO" in header
    assert "VALOR TOTAL" in header


def test_serializar_estruturado_quatro_linhas_por_item():
    m = montar_memorial("A", "Sem", "Biofílico", "X", _linhas(2, "Sem"))
    rows = serializar_estruturado(m, "biofilico")
    labels = [r[5] for r in rows if len(r) > 5 and r[5] in
              ("Largura", "Altura", "Profundidade", "Acabamento")]
    # multiplo de 4 (4 por item) e > 0
    assert labels.count("Largura") == labels.count("Acabamento")
    assert labels.count("Largura") >= 10


def test_serializar_estruturado_tem_total_categoria_e_dois_totais():
    m = montar_memorial("A", "Garden", "Biofílico", "X", _linhas(4, "Garden"))
    rows = serializar_estruturado(m, "biofilico")
    flat = [c for r in rows for c in r]
    assert any("TOTAL MARCENARIA" in c for c in flat)
    assert any("Taxa Decor" in c for c in flat)
    assert any("sem jacuzzi" in c for c in flat)
    assert any("com jacuzzi" in c for c in flat)
```

- [ ] **Step 2: Rodar pra confirmar falha**

Run: `python -m pytest tests/test_memorial_estruturado.py -q`
Expected: FAIL (`serializar_estruturado` não existe / assinatura de `itens_para_tipologia` sem `estilo`).

- [ ] **Step 3: Reescrever `montar_orcamento.py`**

```python
"""Gera memorial descritivo de decor por tipologia (pacote Plus), estrutura oficial.

Uso:
  python montar_orcamento.py --tipologias t.json --produtos p.json \
    --estilo biofilico --spot "Bonito Spot"

Saida (stdout): JSON {memoriais: [...], resumo: [...]}
"""
import argparse
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import LinhaMemorial, MemorialTipologia, Produto
from acabamentos import acabamento_de, META_ITEM
from servicos import SERVICOS

# (role, categoria, codigo_default, descricao, valor_default)
_ITENS_PLUS = [
    ("gabinete_inferior",   "MARCENARIA",      "MRC0002",  "Gabinete inferior (gavetão como vassoureiro)", 3300.0),
    ("gabinete_superior",   "MARCENARIA",      "MRC0011",  "Gabinete superior com LED",                   1100.0),
    ("cabeceira",           "MARCENARIA",      "MRC0038",  "Cabeceira",                                   5800.0),
    ("arara_roupas",        "MARCENARIA",      "MRC0028",  "Arara de roupas",                             2000.0),
    ("bancada_refeicao",    "MARCENARIA",      "MRC0022",  "Mesa/bancada de refeição",                     800.0),
    ("movel_apoio",         "MARCENARIA",      "MRC0020",  "Móvel de apoio",                              1000.0),
    ("prateleira_banheiro", "MARCENARIA",      "MRC0022b", "Prateleira banheiro",                          450.0),
    ("bancada_coz_pedra",   "MARMORARIA",      "MRM0007",  "Bancada cozinha",                             2470.0),
    ("bancada_ban_pedra",   "MARMORARIA",      "MRM0016",  "Bancada banheiro",                            1499.0),
    ("cama_queen",          "MOBILIÁRIO",      "MOB0001",  "Cama box Queen size (c/ auxiliar)",           3986.0),
    ("sofa_cama",           "MOBILIÁRIO",      "MOB0003",  "Sofá-cama",                                   4373.0),
    ("puff",                "MOBILIÁRIO",      "MOB0004",  "Puff",                                         680.0),
    ("cadeira_jantar",      "MOBILIÁRIO",      "MOB0005",  "Cadeira de jantar",                            639.0),
    ("torneira_coz",        "METAIS E INOX",   "LEM0007",  "Torneira de mesa cozinha",                    324.0),
    ("cuba_coz",            "METAIS E INOX",   "LEM0018",  "Cuba de embutir inox cozinha",                284.0),
    ("cuba_ban",            "METAIS E INOX",   "LEM0020",  "Cuba de apoio banheiro",                      180.0),
    ("torneira_ban",        "METAIS E INOX",   "LEM0012",  "Torneira banheiro bica alta",                 289.0),
    ("box_banheiro",        "METAIS E INOX",   "VDR0004",  "Box reto banheiro",                           983.0),
    ("filtro_agua",         "METAIS E INOX",   "LEM0027",  "Filtro de água 3M",                           163.0),
    ("toalheiro_termico",   "METAIS E INOX",   "LEM0013",  "Toalheiro térmico",                           923.0),
    ("kit_metais",          "METAIS E INOX",   "LEM0001",  "Kit de metais",                               222.0),
    ("cooktop",             "ELETROS",         "ELE0006",  "Cooktop vitrocerâmico 2 bocas",               899.0),
    ("frigobar",            "ELETROS",         "ELE0003",  "Frigobar retrô",                             1949.0),
    ("microondas",          "ELETROS",         "ELE0007",  "Microondas 20L Electrolux",                   579.0),
    ("cafeteira",           "ELETROS",         "ELE0019",  "Cafeteira elétrica",                          179.0),
    ("chaleira",            "ELETROS",         "ELE0020",  "Chaleira elétrica",                           189.0),
    ("liquidificador",      "ELETROS",         "ELE0022",  "Liquidificador 1,5L",                         319.0),
    ("depurador",           "ELETROS",         "ELE0014",  "Depurador",                                   799.0),
    ("mini_grill",          "ELETROS",         "ELE0024",  "Mini grill e sanduicheira",                   159.0),
    ("tv",                  "ELETROS",         "ELE0001",  'Smart TV 43"',                               1599.0),
    ("iluminacao",          "ILUMINAÇÃO",      "ILU0001",  "Kit iluminação",                              347.0),
    ("jacuzzi",             "ÁREA EXTERNA",    "EXT0001",  "Jacuzzi circular Ø 1,80m",                  5000.0),
    ("mesa_externa",        "ÁREA EXTERNA",    "EXT0002",  "Mesa externa redonda + cadeiras",            1500.0),
]

_CADEIRAS_POR_CAP: dict[int, int] = {2: 2, 3: 3, 4: 3, 5: 4}
_TERRACO_GARDEN  = {"garden", "terraço", "terraco"}
_TERRACO_VARANDA = {"varanda", "sacada"}

_COLUNAS = ["", "ITEM/TIPO", "AMBIENTE", "IMAGEM", "ITEM", "FICHA TÉCNICA", "",
            "FORNECEDOR", "QUANT.", "REFERÊNCIA", "VALOR UNITÁRIO", "VALOR TOTAL"]


def itens_para_tipologia(
    capacidade: int,
    terraco: str,
    tipo: str,
    produtos: dict,
    estilo: str = "biofilico",
) -> list[LinhaMemorial]:
    t = terraco.strip().lower()
    eh_garden  = t in _TERRACO_GARDEN
    eh_varanda = t in _TERRACO_VARANDA
    eh_pcd     = tipo.strip().lower() == "pcd"

    linhas: list[LinhaMemorial] = []
    for (role, categoria, codigo, descricao, valor_default) in _ITENS_PLUS:
        if role == "sofa_cama"    and capacidade not in (4, 5): continue
        if role == "jacuzzi"      and not eh_garden:            continue
        if role == "mesa_externa" and not eh_varanda:           continue

        qty = _CADEIRAS_POR_CAP.get(capacidade, 2) if role == "cadeira_jantar" else 1

        if codigo in produtos:
            p = produtos[codigo]
            valor = p.valor_unitario if isinstance(p, Produto) else p.get("valor_unitario", valor_default)
        else:
            valor = valor_default

        nome = f"{descricao} (PCD)" if (
            eh_pcd and "banheiro" in descricao.lower() and "bancada" not in descricao.lower()
        ) else descricao

        linhas.append(LinhaMemorial(
            categoria=categoria, item=nome, quantidade=qty, valor_unitario=valor,
            ambiente=META_ITEM.get(role, {}).get("ambiente", ""),
            referencia=codigo, acabamento=acabamento_de(estilo, role),
            opcional=(role == "jacuzzi"),
        ))

    # Serviços (INSUMOS)
    for (role, nome, ambiente, codigo, valor_default) in SERVICOS:
        linhas.append(LinhaMemorial(
            categoria="INSUMOS", item=nome, quantidade=1, valor_unitario=valor_default,
            ambiente=ambiente, referencia=codigo, acabamento="N/A",
        ))
    return linhas


def montar_memorial(tipologia, descricao, estilo, spot, linhas) -> MemorialTipologia:
    return MemorialTipologia(tipologia=tipologia, descricao=descricao,
                             estilo=estilo, spot=spot, linhas=linhas)


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def serializar_estruturado(memorial: MemorialTipologia, estilo: str) -> list[list]:
    """Matriz de 11 colunas no formato oficial (categoria/ambiente 'mescladas',
    4 linhas por item, TOTAL por categoria, taxas e dois totais)."""
    rows: list[list] = []
    rows.append(["", "MEMORIAL DESCRITIVO", memorial.spot, "", "",
                 f"{memorial.tipologia} — {memorial.descricao}", "", "",
                 f"Estilo: {memorial.estilo}", "Pacote: Plus", "", ""])
    rows.append(list(_COLUNAS))

    cat_atual = None
    amb_atual = None
    # agrupa preservando a ordem de inserção das linhas
    for l in memorial.linhas:
        cat_cell = ""
        amb_cell = ""
        if l.categoria != cat_atual:
            cat_atual = l.categoria
            amb_atual = None
            cat_cell = l.categoria
        if l.ambiente != amb_atual:
            amb_atual = l.ambiente
            amb_cell = l.ambiente
        # 4 linhas (ficha técnica)
        rows.append(["", cat_cell, amb_cell, "", l.item, "Largura", l.largura,
                     l.fornecedor, l.quantidade, l.referencia,
                     _brl(l.valor_unitario), _brl(l.valor_total)])
        rows.append(["", "", "", "", "", "Altura", l.altura, "", "", "", "", ""])
        rows.append(["", "", "", "", "", "Profundidade", l.profundidade, "", "", "", "", ""])
        rows.append(["", "", "", "", "", "Acabamento", l.acabamento, "", "", "", "", ""])

    # TOTAL por categoria (na ordem em que aparecem)
    vistas: list[str] = []
    for l in memorial.linhas:
        if l.categoria not in vistas:
            vistas.append(l.categoria)
    rows.append([""] * 12)
    for cat in vistas:
        rows.append(["", f"TOTAL {cat}", "", "", "", "", "", "", "", "",
                     _brl(memorial.subtotais[cat]), ""])

    rows.append([""] * 12)
    rows.append(["", "Valor Produtos (sem jacuzzi)", "", "", "", "", "", "", "", "",
                 _brl(memorial.valor_produtos), ""])
    rows.append(["", "Taxa Decor", "", "", "", "", "", "", "", "", _brl(memorial.taxa_decor), ""])
    rows.append(["", "Taxa Adm (13%)", "", "", "", "", "", "", "", "", _brl(memorial.taxa_adm), ""])
    rows.append(["", "TOTAL (sem jacuzzi)", "", "", "", "", "", "", "", "",
                 _brl(memorial.total_geral), ""])
    rows.append(["", "TOTAL (com jacuzzi)", "", "", "", "", "", "", "", "",
                 _brl(memorial.total_com_jacuzzi), ""])
    return rows


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Gera memoriais de decor por tipologia (Plus)")
    p.add_argument("--tipologias", type=Path, required=True)
    p.add_argument("--produtos", type=Path)
    p.add_argument("--estilo", required=True, choices=["clean", "biofilico", "industrial", "bruma"])
    p.add_argument("--spot", required=True)
    args = p.parse_args()

    tipologias = json.loads(args.tipologias.read_text(encoding="utf-8"))
    produtos: dict = {}
    if args.produtos:
        raw = json.loads(args.produtos.read_text(encoding="utf-8"))
        produtos = {k: Produto(k, v["nome"], v["categoria"], v["valor_unitario"], v.get("unidade", "un"))
                    for k, v in raw.items()}

    memoriais = []
    for t in tipologias:
        letra = t["tipologia"]
        terraco_label = "Sem terraço" if t["terraco"].strip().lower() == "sem" else t["terraco"]
        descr = f"{terraco_label} · {t['tipo']} · Cap. {t['capacidade']}"
        linhas = itens_para_tipologia(t["capacidade"], t["terraco"], t["tipo"], produtos,
                                      estilo=args.estilo)
        m = montar_memorial(letra, descr, args.estilo.capitalize(), args.spot, linhas)
        memoriais.append({
            "tipologia": letra, "descricao": descr,
            "total_geral": m.total_geral, "total_com_jacuzzi": m.total_com_jacuzzi,
            "valor_produtos": m.valor_produtos, "valor_opcionais": m.valor_opcionais,
            "taxa_adm": m.taxa_adm, "taxa_decor": m.taxa_decor, "subtotais": m.subtotais,
            "linhas": [
                {"categoria": l.categoria, "ambiente": l.ambiente, "item": l.item,
                 "quantidade": l.quantidade, "valor_unitario": l.valor_unitario,
                 "valor_total": l.valor_total, "referencia": l.referencia,
                 "acabamento": l.acabamento, "fornecedor": l.fornecedor, "opcional": l.opcional}
                for l in m.linhas
            ],
            "rows": serializar_estruturado(m, args.estilo),
        })

    resumo = [{"tipologia": x["tipologia"], "descricao": x["descricao"],
               "total_geral": x["total_geral"]} for x in memoriais]
    print(json.dumps({"memoriais": memoriais, "resumo": resumo}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar os testes novos**

Run: `python -m pytest tests/test_memorial_estruturado.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add skills/orcamento-decor/scripts/montar_orcamento.py tests/test_memorial_estruturado.py
git commit -m "feat(memorial): itens enriquecidos + serviços + serializador estruturado"
```

---

## Task 5: Ajustar testes antigos de montar_orcamento

**Files:**
- Modify: `tests/test_montar_orcamento.py`

Os testes antigos assumem categoria "LOUÇAS E METAIS" (agora "METAIS E INOX"), `serializar_csv` (removido) e jacuzzi no total. Ajustar.

- [ ] **Step 1: Substituir os testes que quebraram**

Abrir `tests/test_montar_orcamento.py` e aplicar:
- Trocar `from montar_orcamento import itens_para_tipologia, montar_memorial, serializar_csv` por `from montar_orcamento import itens_para_tipologia, montar_memorial, serializar_estruturado`.
- Em `test_sempre_tem_categorias_obrigatorias`: trocar `"LOUÇAS E METAIS"` por `"METAIS E INOX"`.
- Remover os 4 testes `test_csv_*` (cabecalho/total/taxa/spot) e substituir por:

```python
def test_estruturado_contem_total_geral():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    flat = [c for r in serializar_estruturado(m, "clean") for c in r]
    assert any("TOTAL (sem jacuzzi)" in c for c in flat)

def test_estruturado_contem_nome_spot():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    flat = [c for r in serializar_estruturado(m, "clean") for c in r]
    assert any("Natal Spot" in str(c) for c in flat)
```

- Em `test_cap5_garden_total_maior_que_cap2_sem`: continua válido (cap5 tem sofá-cama + cadeiras a mais → base maior), manter.
- Em `test_subtotais_batem_com_soma_das_linhas`: continua válido (subtotais somam todas as linhas), manter.

- [ ] **Step 2: Rodar a suite inteira**

Run: `python -m pytest tests/ -q`
Expected: tudo passa (Fase 1 + ler_catalogo + gerar_dashboard_js + acabamentos + memorial_estruturado + montar_orcamento ajustado).

- [ ] **Step 3: Commit**

```bash
git add tests/test_montar_orcamento.py
git commit -m "test(memorial): ajusta testes antigos ao formato estruturado"
```

---

## Task 6: gerar_xlsx.py — .xlsx multi-aba a partir das matrizes

**Files:**
- Create: `skills/orcamento-decor/scripts/gerar_xlsx.py`

- [ ] **Step 1: Escrever `skills/orcamento-decor/scripts/gerar_xlsx.py`**

```python
"""Monta um .xlsx multi-aba (uma aba por tipologia + Resumo) a partir do JSON de montar_orcamento.

Uso:
  python montar_orcamento.py ... > memoriais.json
  python gerar_xlsx.py --memoriais memoriais.json --spot "Bonito Spot" --saida saida.xlsx
"""
import argparse
import json
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

NAVY = "FF000C3C"
bold = Font(bold=True)
bold_white = Font(bold=True, color="FFFFFFFF")
navy_fill = PatternFill("solid", fgColor=NAVY)


def _aba(ws, rows):
    for r in rows:
        ws.append(r)
    # cabeçalho (linha 2) em navy
    for c in ws[2]:
        c.font = bold_white
        c.fill = navy_fill
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["E"].width = 42
    ws.column_dimensions["F"].width = 14
    ws.column_dimensions["G"].width = 22
    for col in ("H", "I", "J", "K", "L"):
        ws.column_dimensions[col].width = 16


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--memoriais", type=Path, required=True)
    p.add_argument("--spot", required=True)
    p.add_argument("--saida", type=Path, required=True)
    args = p.parse_args()

    data = json.loads(args.memoriais.read_text(encoding="utf-8"))
    wb = Workbook()

    # Resumo
    ws = wb.active
    ws.title = "Resumo"
    ws.append([f"{args.spot} — Orçamento Decor (Plus)"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append([])
    ws.append(["TIPOLOGIA", "DESCRIÇÃO", "CUSTO ESTIMADO (sem jacuzzi)", "COM JACUZZI"])
    for c in ws[3]:
        c.font = bold_white
        c.fill = navy_fill
    for m in data["memoriais"]:
        ws.append([m["tipologia"], m["descricao"], m["total_geral"], m["total_com_jacuzzi"]])
        ws.cell(row=ws.max_row, column=3).number_format = 'R$ #,##0.00'
        ws.cell(row=ws.max_row, column=4).number_format = 'R$ #,##0.00'
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 32
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["D"].width = 18

    # Uma aba por tipologia
    for m in data["memoriais"]:
        aba = wb.create_sheet(title=f"Tipologia {m['tipologia']}")
        _aba(aba, m["rows"])

    wb.save(args.saida)
    print(f"xlsx salvo: {args.saida} | abas: {wb.sheetnames}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke test (gera xlsx do Bonito)**

```bash
printf '%s' '[{"tipologia":"A","terraco":"Garden","tipo":"Padrão","capacidade":2},{"tipologia":"D","terraco":"Sem sacada","tipo":"Padrão","capacidade":2}]' > tmp/bonito2.json
python skills/orcamento-decor/scripts/montar_orcamento.py --tipologias tmp/bonito2.json --estilo biofilico --spot "Bonito Spot" > tmp/mem2.json
python skills/orcamento-decor/scripts/gerar_xlsx.py --memoriais tmp/mem2.json --spot "Bonito Spot" --saida tmp/teste.xlsx
```
Expected: `xlsx salvo: ... | abas: ['Resumo', 'Tipologia A', 'Tipologia D']`. Abrir e conferir 11 colunas + 4 linhas/item + TOTAL por categoria + dois totais.

- [ ] **Step 3: Commit**

```bash
git add skills/orcamento-decor/scripts/gerar_xlsx.py
git commit -m "feat(memorial): gerar_xlsx.py - .xlsx multi-aba no formato estruturado"
```

---

## Task 7: Reference doc + SKILL.md + re-sync + suite

**Files:**
- Create: `skills/orcamento-decor/references/acabamentos-por-estilo.md`
- Modify: `skills/orcamento-decor/SKILL.md`

- [ ] **Step 1: Criar `skills/orcamento-decor/references/acabamentos-por-estilo.md`**

```markdown
# Paleta de acabamento por estilo

Embutida em `scripts/acabamentos.py` (`_ACABAMENTO` + `_ACABAMENTO_FIXO`). Calibrável.

- **Biofílico**: calibrado do memorial-exemplo da Raquel (Mdf areia/savana/palhinha, metal bege claro, granito pitaya, suede preto).
- **Clean**: madeira clara/branco, metal cromado, granito branco.
- **Industrial**: Mdf grafite/carvalho, metal preto, granito preto, couro caramelo.
- **Bruma**: Mdf fendi/cinza, metal champagne, granito cinza, linho areia.
- **Metais/eletros** (`_ACABAMENTO_FIXO`): independem do estilo (cromado, inox, preto...).
- Fallback: "A confirmar".

Para recalibrar, ajustar os dicts em `acabamentos.py` conforme os moodboards
(IDs no SKILL.md) e o Sheet de marcenaria por estilo (`1VnEZ-2UscCx03cwEGEDVA9vbfaUw4Y04wiM_lh9YRYI`).
```

- [ ] **Step 2: Atualizar o passo 5 e 6 do `SKILL.md`**

Em `skills/orcamento-decor/SKILL.md`, no passo "### 5. Gerar memoriais", após o comando do `montar_orcamento.py`, acrescentar:

````markdown

O JSON traz, por tipologia, o campo `rows` (matriz de 11 colunas no formato oficial) e os totais `total_geral` (sem jacuzzi) e `total_com_jacuzzi`.

Gere o .xlsx multi-aba (uma aba por tipologia + Resumo):
```bash
python skills/orcamento-decor/scripts/gerar_xlsx.py \
  --memoriais tmp/memoriais.json --spot "SPOT_NAME" --saida tmp/Orcamento_SPOT.xlsx
```
````

E no passo "### 6", trocar o destino e o formato:
- Pasta destino: **`10 - Projeto de Interiores / 03 - Memorial descritivo`** (não mais `02 - Imagens`).
- Subir o `.xlsx` via `create_file` (base64) com `contentMimeType` de planilha e conversão pra Google Sheet — **um único arquivo, abas por tipologia** (não um Sheet por tipologia).

- [ ] **Step 3: Rodar a suite completa**

Run: `python -m pytest tests/ -q`
Expected: tudo verde.

- [ ] **Step 4: Re-instalar a skill globalmente**

```powershell
$src = "C:\Users\Seazone\Claude\seazone\hackathon-investimentos\skills\orcamento-decor"
$dst = "C:\Users\Seazone\Claude\.claude\skills\orcamento-decor"
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item $src $dst -Recurse
```

- [ ] **Step 5: Commit**

```bash
git add skills/orcamento-decor/references/acabamentos-por-estilo.md skills/orcamento-decor/SKILL.md
git commit -m "docs(memorial): acabamentos-por-estilo + SKILL.md (xlsx multi-aba em 03 - Memorial descritivo)"
```

---

## Validação pós-implementação

1. `python -m pytest tests/ -q` tudo verde.
2. Gerar o xlsx do Bonito (6 tipologias) e conferir: 11 colunas, 4 linhas/item, ambiente/acabamento por estilo preenchidos, TOTAL por categoria, Taxa Decor/Adm, dois totais (sem/com jacuzzi), aba Resumo.
3. Acabamento muda ao trocar `--estilo` (biofilico vs industrial).
4. Quando o conector Drive estiver na conta da Raquel: subir o xlsx único em `03 - Memorial descritivo` e atualizar `orcamentos.js`.
