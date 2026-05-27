# Orçamento Decor (Fase 2) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a skill `orcamento-decor` — skill independente que, dado um Spot com tipologias já geradas, produz um memorial descritivo de decor (pacote Plus) por tipologia com preços do catálogo real, gerando Sheets no Drive.

**Architecture:** 3 scripts Python puros testáveis (`modelos.py`, `ler_catalogo.py`, `montar_orcamento.py`) + `SKILL.md` que orquestra Drive MCP. O Claude executa os scripts e faz as chamadas Drive. Nenhum arquivo da skill `tabela-tipologias` é tocado.

**Tech Stack:** Python 3.12 stdlib (`csv`, `json`, `io`, `argparse`), pytest, Drive MCP (Composio)

---

## File Structure

```
skills/orcamento-decor/          ← tudo novo, não toca tabela-tipologias
  SKILL.md
  scripts/
    modelos.py                   # dataclasses: Produto, LinhaMemorial, MemorialTipologia
    ler_catalogo.py              # CSV db002_produtos → dict[str, Produto]
    montar_orcamento.py          # core: tipologias + produtos → memoriais + CSV
  references/
    itens-por-capacidade.md      # regras de negócio documentadas
    catalogo-schema.md           # preenchido na 1ª execução real

tests/
  fixtures/
    catalogo_sample.csv          # fixture pra testes (nova)
  test_ler_catalogo.py           # novo
  test_montar_orcamento.py       # novo

dashboard/data/tipologias.js     # ganha campo `estilo` por spot (quando skill roda)
```

---

## Task 1: Estrutura de pastas + modelos.py

**Files:**
- Create: `skills/orcamento-decor/scripts/modelos.py`
- Create dirs: `skills/orcamento-decor/scripts/`, `skills/orcamento-decor/references/`

- [ ] **Criar pastas**

```powershell
New-Item -ItemType Directory -Force "skills/orcamento-decor/scripts"
New-Item -ItemType Directory -Force "skills/orcamento-decor/references"
```

- [ ] **Escrever `skills/orcamento-decor/scripts/modelos.py`**

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

    @property
    def valor_total(self) -> float:
        return round(self.quantidade * self.valor_unitario, 2)


@dataclass
class MemorialTipologia:
    tipologia: str   # ex: "A"
    descricao: str   # ex: "Sem Sacada · Padrão · Cap. 4"
    estilo: str      # ex: "Clean"
    spot: str        # ex: "Natal Spot"
    linhas: list[LinhaMemorial] = field(default_factory=list)
    taxa_decor: float = 2500.0

    @property
    def valor_produtos(self) -> float:
        return round(sum(l.valor_total for l in self.linhas), 2)

    @property
    def taxa_adm(self) -> float:
        return round(self.valor_produtos * 0.13, 2)

    @property
    def subtotais(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for l in self.linhas:
            result[l.categoria] = round(result.get(l.categoria, 0.0) + l.valor_total, 2)
        return result

    @property
    def total_geral(self) -> float:
        return round(self.valor_produtos + self.taxa_decor + self.taxa_adm, 2)
```

- [ ] **Commit**

```bash
git add skills/orcamento-decor/scripts/modelos.py
git commit -m "feat(orcamento): dataclasses compartilhados (modelos.py)"
```

---

## Task 2: ler_catalogo.py + testes

**Files:**
- Create: `skills/orcamento-decor/scripts/ler_catalogo.py`
- Create: `tests/fixtures/catalogo_sample.csv`
- Create: `tests/test_ler_catalogo.py`

- [ ] **Criar fixture `tests/fixtures/catalogo_sample.csv`**

```csv
codigo,nome,categoria,valor_unitario,unidade
MRC0002,Gabinete inferior,MARCENARIA,3300.00,un
MOB0001,Cama Box Queen,MOBILIÁRIO,3986.44,un
ELE0006,Cooktop vitrocerâmico,ELETROS,899.00,un
LEM0007,Torneira cozinha,LOUÇAS E METAIS,324.90,un
SEM_PRECO,Produto sem preço,ELETROS,,un
REAIS,Item em reais,MOBILIÁRIO,"R$ 1.234,56",un
```

- [ ] **Escrever `tests/test_ler_catalogo.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from ler_catalogo import parsear_csv
from modelos import Produto

FIXTURE = (Path(__file__).parent / "fixtures/catalogo_sample.csv").read_text(encoding="utf-8")


def test_parseia_produto_marcenaria():
    produtos = parsear_csv(FIXTURE)
    assert "MRC0002" in produtos
    p = produtos["MRC0002"]
    assert p.nome == "Gabinete inferior"
    assert p.categoria == "MARCENARIA"
    assert p.valor_unitario == 3300.0
    assert p.unidade == "un"


def test_parseia_todos_os_codigos():
    produtos = parsear_csv(FIXTURE)
    assert set(produtos.keys()) == {"MRC0002", "MOB0001", "ELE0006", "LEM0007",
                                    "SEM_PRECO", "REAIS"}


def test_valor_ausente_vira_zero():
    produtos = parsear_csv(FIXTURE)
    assert produtos["SEM_PRECO"].valor_unitario == 0.0


def test_aceita_valor_formatado_em_reais():
    produtos = parsear_csv(FIXTURE)
    assert produtos["REAIS"].valor_unitario == 1234.56


def test_erro_se_coluna_obrigatoria_ausente():
    import pytest
    csv_ruim = "nome,valor\nItem A,100\n"
    with pytest.raises(ValueError, match="Colunas não encontradas"):
        parsear_csv(csv_ruim)


def test_mapeamento_manual_de_colunas():
    csv_custom = "Ref,Produto,Grupo,Preco\nXX01,Mesa,MOBILIÁRIO,500.00\n"
    produtos = parsear_csv(csv_custom, {
        "codigo": "Ref", "nome": "Produto",
        "categoria": "Grupo", "valor_unitario": "Preco",
    })
    assert "XX01" in produtos
    assert produtos["XX01"].valor_unitario == 500.0
```

- [ ] **Rodar pra confirmar falha**

```bash
python -m pytest tests/test_ler_catalogo.py -v
```
Esperado: `ModuleNotFoundError: No module named 'ler_catalogo'`

- [ ] **Escrever `skills/orcamento-decor/scripts/ler_catalogo.py`**

```python
"""Parseia CSV do db002_produtos (exportado do Drive) → dict[str, Produto].

Uso:
  python ler_catalogo.py --csv caminho/db002.csv > produtos.json
  cat db002.csv | python ler_catalogo.py > produtos.json
  python ler_catalogo.py --csv db002.csv --col-codigo Ref --col-valor_unitario Price
"""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import Produto

COLUNAS_PADRAO = {
    "codigo":         ["codigo", "código", "cod", "id", "referencia", "ref", "sku"],
    "nome":           ["nome", "descricao", "descrição", "produto", "item", "name"],
    "categoria":      ["categoria", "categoria_produto", "tipo", "grupo", "category"],
    "valor_unitario": ["valor_unitario", "valor unitário", "preco", "preço", "price",
                       "valor", "vl_unitario"],
    "unidade":        ["unidade", "un", "unid", "unit"],
}


def _encontrar_coluna(headers: list[str], alternativas: list[str]) -> str | None:
    hl = [h.lower().strip() for h in headers]
    for alt in alternativas:
        if alt.lower() in hl:
            return headers[hl.index(alt.lower())]
    return None


def _parse_valor(s: str) -> float:
    if not s or s.strip() in ("", "-", "N/A", "n/a"):
        return 0.0
    s = s.strip().lstrip("R$").strip().strip('"')
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def parsear_csv(
    texto_csv: str,
    mapeamento: dict[str, str] | None = None,
) -> dict[str, Produto]:
    reader = csv.DictReader(io.StringIO(texto_csv))
    headers = list(reader.fieldnames or [])

    mapa = dict(mapeamento or {})
    for campo, alternativas in COLUNAS_PADRAO.items():
        if campo not in mapa:
            col = _encontrar_coluna(headers, alternativas)
            if col:
                mapa[campo] = col

    faltando = [c for c in ("codigo", "nome", "categoria", "valor_unitario")
                if c not in mapa]
    if faltando:
        raise ValueError(
            f"Colunas não encontradas: {faltando}. "
            f"Disponíveis: {headers}. "
            f"Use --col-<campo> para mapear manualmente."
        )

    produtos: dict[str, Produto] = {}
    for row in reader:
        codigo = row.get(mapa["codigo"], "").strip()
        if not codigo:
            continue
        col_unidade = mapa.get("unidade", "__NA__")
        produtos[codigo] = Produto(
            codigo=codigo,
            nome=row.get(mapa["nome"], "").strip(),
            categoria=row.get(mapa["categoria"], "").strip().upper(),
            valor_unitario=_parse_valor(row.get(mapa["valor_unitario"], "")),
            unidade=row.get(col_unidade, "un").strip() or "un",
        )
    return produtos


def main() -> None:
    p = argparse.ArgumentParser(description="Parseia CSV do db002_produtos → JSON")
    p.add_argument("--csv", type=Path, help="Caminho do CSV (default: stdin)")
    for campo in COLUNAS_PADRAO:
        p.add_argument(f"--col-{campo}", dest=f"col_{campo}",
                       help=f"Nome da coluna para '{campo}' (auto-detectado se omitido)")
    args = p.parse_args()

    texto = args.csv.read_text(encoding="utf-8-sig") if args.csv else sys.stdin.read()
    mapeamento = {
        campo: getattr(args, f"col_{campo}")
        for campo in COLUNAS_PADRAO
        if getattr(args, f"col_{campo}") is not None
    }

    try:
        produtos = parsear_csv(texto, mapeamento or None)
        saida = {
            k: {"nome": v.nome, "categoria": v.categoria,
                "valor_unitario": v.valor_unitario, "unidade": v.unidade}
            for k, v in produtos.items()
        }
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    except ValueError as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Rodar e confirmar que passa**

```bash
python -m pytest tests/test_ler_catalogo.py -v
```
Esperado:
```
tests/test_ler_catalogo.py::test_parseia_produto_marcenaria PASSED
tests/test_ler_catalogo.py::test_parseia_todos_os_codigos PASSED
tests/test_ler_catalogo.py::test_valor_ausente_vira_zero PASSED
tests/test_ler_catalogo.py::test_aceita_valor_formatado_em_reais PASSED
tests/test_ler_catalogo.py::test_erro_se_coluna_obrigatoria_ausente PASSED
tests/test_ler_catalogo.py::test_mapeamento_manual_de_colunas PASSED
6 passed
```

- [ ] **Commit**

```bash
git add skills/orcamento-decor/scripts/ler_catalogo.py tests/fixtures/catalogo_sample.csv tests/test_ler_catalogo.py
git commit -m "feat(orcamento): ler_catalogo.py + testes"
```

---

## Task 3: montar_orcamento.py — testes (TDD primeiro)

**Files:**
- Create: `tests/test_montar_orcamento.py`

Escrever TODOS os testes antes da implementação. Todos devem falhar.

- [ ] **Criar `tests/test_montar_orcamento.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from montar_orcamento import itens_para_tipologia, montar_memorial, serializar_csv
from modelos import LinhaMemorial, MemorialTipologia, Produto

PRODUTOS_VAZIO: dict = {}


def _categorias(linhas: list[LinhaMemorial]) -> set[str]:
    return {l.categoria for l in linhas}


def _item_presente(linhas: list[LinhaMemorial], substr: str) -> bool:
    return any(substr.lower() in l.item.lower() for l in linhas)


def _qtd_de(linhas: list[LinhaMemorial], substr: str) -> int:
    return sum(l.quantidade for l in linhas if substr.lower() in l.item.lower())


# ── Itens fixos ──────────────────────────────────────────────────────────────

def test_sempre_tem_gabinete_inferior():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "gabinete inferior")

def test_sempre_tem_cama_queen():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "cama")

def test_sempre_tem_cooktop():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "cooktop")

def test_sempre_tem_categorias_obrigatorias():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    cats = _categorias(linhas)
    assert "MARCENARIA" in cats
    assert "MARMORARIA" in cats
    assert "ELETROS" in cats
    assert "LOUÇAS E METAIS" in cats


# ── Sofá-cama (cap 4 e 5) ───────────────────────────────────────────────────

def test_cap2_sem_sofa_cama():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "sofá-cama")

def test_cap3_sem_sofa_cama():
    linhas = itens_para_tipologia(3, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "sofá-cama")

def test_cap4_tem_sofa_cama():
    linhas = itens_para_tipologia(4, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "sofá-cama")

def test_cap5_tem_sofa_cama():
    linhas = itens_para_tipologia(5, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "sofá-cama")


# ── Área externa ─────────────────────────────────────────────────────────────

def test_sem_terraco_nao_tem_jacuzzi():
    linhas = itens_para_tipologia(4, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "jacuzzi")

def test_garden_tem_jacuzzi():
    linhas = itens_para_tipologia(4, "Garden", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "jacuzzi")

def test_terraco_tipo_tem_jacuzzi():
    linhas = itens_para_tipologia(4, "Terraço", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "jacuzzi")

def test_garden_nao_tem_mesa_externa():
    linhas = itens_para_tipologia(4, "Garden", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "mesa externa")

def test_sacada_tem_mesa_externa():
    linhas = itens_para_tipologia(5, "Sacada", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "mesa externa")

def test_varanda_tem_mesa_externa():
    linhas = itens_para_tipologia(3, "Varanda", "Padrão", PRODUTOS_VAZIO)
    assert _item_presente(linhas, "mesa externa")

def test_sacada_nao_tem_jacuzzi():
    linhas = itens_para_tipologia(5, "Sacada", "Padrão", PRODUTOS_VAZIO)
    assert not _item_presente(linhas, "jacuzzi")


# ── PCD ──────────────────────────────────────────────────────────────────────

def test_pcd_marca_banheiro_como_pcd():
    linhas = itens_para_tipologia(2, "Sem", "PCD", PRODUTOS_VAZIO)
    assert any("PCD" in l.item for l in linhas)


# ── Cadeiras ─────────────────────────────────────────────────────────────────

def test_cadeiras_cap2_qty2():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 2

def test_cadeiras_cap3_qty3():
    linhas = itens_para_tipologia(3, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 3

def test_cadeiras_cap4_qty3():
    linhas = itens_para_tipologia(4, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 3

def test_cadeiras_cap5_qty4():
    linhas = itens_para_tipologia(5, "Sem", "Padrão", PRODUTOS_VAZIO)
    assert _qtd_de(linhas, "cadeira") == 4


# ── Catálogo sobrescreve preço ────────────────────────────────────────────────

def test_catalogo_sobrescreve_preco_default():
    produtos = {"MRC0002": Produto("MRC0002", "Gabinete inferior", "MARCENARIA", 9999.0)}
    linhas = itens_para_tipologia(2, "Sem", "Padrão", produtos)
    gab = next(l for l in linhas if "gabinete inferior" in l.item.lower())
    assert gab.valor_unitario == 9999.0


# ── Cálculos ─────────────────────────────────────────────────────────────────

def test_subtotais_batem_com_soma_das_linhas():
    linhas = itens_para_tipologia(4, "Garden", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Garden · Padrão · Cap. 4", "Clean", "Natal Spot", linhas)
    for cat, subtotal in m.subtotais.items():
        esperado = round(sum(l.valor_total for l in m.linhas if l.categoria == cat), 2)
        assert subtotal == esperado, f"Subtotal {cat}: {subtotal} != {esperado}"

def test_taxa_adm_e_13_porcento():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.taxa_adm == round(m.valor_produtos * 0.13, 2)

def test_total_geral_soma_correta():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.total_geral == round(m.valor_produtos + m.taxa_decor + m.taxa_adm, 2)

def test_taxa_decor_fixo_2500():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    assert m.taxa_decor == 2500.0

def test_cap5_garden_total_maior_que_cap2_sem():
    l2 = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    l5 = itens_para_tipologia(5, "Garden", "Padrão", PRODUTOS_VAZIO)
    m2 = montar_memorial("A", "", "Clean", "X", l2)
    m5 = montar_memorial("B", "", "Clean", "X", l5)
    assert m5.total_geral > m2.total_geral


# ── CSV ───────────────────────────────────────────────────────────────────────

def test_csv_contem_cabecalho_item():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "ITEM" in csv_text

def test_csv_contem_total_geral():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "TOTAL GERAL" in csv_text

def test_csv_contem_taxa_decor():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "Taxa Decor" in csv_text

def test_csv_contem_nome_spot():
    linhas = itens_para_tipologia(2, "Sem", "Padrão", PRODUTOS_VAZIO)
    m = montar_memorial("A", "Sem · Padrão · Cap. 2", "Clean", "Natal Spot", linhas)
    csv_text = serializar_csv(m)
    assert "Natal Spot" in csv_text
```

- [ ] **Rodar pra confirmar falha**

```bash
python -m pytest tests/test_montar_orcamento.py -v
```
Esperado: `ModuleNotFoundError: No module named 'montar_orcamento'`

---

## Task 4: montar_orcamento.py — implementação completa

**Files:**
- Create: `skills/orcamento-decor/scripts/montar_orcamento.py`

- [ ] **Criar `skills/orcamento-decor/scripts/montar_orcamento.py`**

```python
"""Gera memorial descritivo de decor por tipologia (pacote Plus).

Uso:
  python montar_orcamento.py --tipologias t.json --produtos p.json \\
    --estilo clean --spot "Natal Spot"

Entrada:
  --tipologias : JSON lista [{tipologia, terraco, tipo, capacidade}]
  --produtos   : JSON de ler_catalogo.py {codigo: {nome, categoria, valor_unitario}}
  --estilo     : clean | biofilico | industrial | bruma
  --spot       : nome do empreendimento

Saída (stdout): JSON {memoriais: [...], resumo: [...]}
"""
import argparse
import csv as csvmodule
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import LinhaMemorial, MemorialTipologia, Produto

# ---------------------------------------------------------------------------
# Tabela de itens — pacote Plus, preços de referência 2026
# (role, categoria, codigo_default, descricao, valor_default)
# Preços do catálogo real (db002_produtos) sobrescrevem estes defaults.
# ---------------------------------------------------------------------------
_ITENS_PLUS = [
    # MARCENARIA
    ("gabinete_inferior",   "MARCENARIA",       "MRC0002",  "Gabinete inferior (gavetão como vassoureiro)", 3300.0),
    ("gabinete_superior",   "MARCENARIA",       "MRC0011",  "Gabinete superior com LED",                   1100.0),
    ("cabeceira",           "MARCENARIA",       "MRC0038",  "Cabeceira",                                   5800.0),
    ("arara_roupas",        "MARCENARIA",       "MRC0028",  "Arara de roupas",                             2000.0),
    ("bancada_refeicao",    "MARCENARIA",       "MRC0022",  "Mesa/bancada de refeição",                     800.0),
    ("movel_apoio",         "MARCENARIA",       "MRC0020",  "Móvel de apoio",                              1000.0),
    ("prateleira_banheiro", "MARCENARIA",       "MRC0022b", "Prateleira banheiro",                          450.0),
    # MARMORARIA
    ("bancada_coz_pedra",   "MARMORARIA",       "MRM0007",  "Bancada cozinha (granito pitaya)",            2470.0),
    ("bancada_ban_pedra",   "MARMORARIA",       "MRM0016",  "Bancada banheiro (granito pitaya)",           1499.0),
    # MOBILIÁRIO
    ("cama_queen",          "MOBILIÁRIO",       "MOB0001",  "Cama box Queen size (c/ auxiliar)",           3986.0),
    ("sofa_cama",           "MOBILIÁRIO",       "MOB0003",  "Sofá-cama",                                   4373.0),
    ("puff",                "MOBILIÁRIO",       "MOB0004",  "Puff",                                         680.0),
    ("cadeira_jantar",      "MOBILIÁRIO",       "MOB0005",  "Cadeira de jantar",                            639.0),
    # LOUÇAS E METAIS
    ("torneira_coz",        "LOUÇAS E METAIS",  "LEM0007",  "Torneira de mesa cozinha",                    324.0),
    ("cuba_coz",            "LOUÇAS E METAIS",  "LEM0018",  "Cuba de embutir inox cozinha",                284.0),
    ("cuba_ban",            "LOUÇAS E METAIS",  "LEM0020",  "Cuba de apoio banheiro",                      180.0),
    ("torneira_ban",        "LOUÇAS E METAIS",  "LEM0012",  "Torneira banheiro bica alta",                 289.0),
    ("box_banheiro",        "LOUÇAS E METAIS",  "VDR0004",  "Box reto banheiro",                           983.0),
    ("filtro_agua",         "LOUÇAS E METAIS",  "LEM0027",  "Filtro de água 3M",                           163.0),
    ("toalheiro_termico",   "LOUÇAS E METAIS",  "LEM0013",  "Toalheiro térmico",                           923.0),
    ("kit_metais",          "LOUÇAS E METAIS",  "LEM0001",  "Kit de metais",                               222.0),
    # ELETROS
    ("cooktop",             "ELETROS",          "ELE0006",  "Cooktop vitrocerâmico 2 bocas",               899.0),
    ("frigobar",            "ELETROS",          "ELE0003",  "Frigobar retrô",                             1949.0),
    ("microondas",          "ELETROS",          "ELE0007",  "Microondas 20L Electrolux",                   579.0),
    ("cafeteira",           "ELETROS",          "ELE0019",  "Cafeteira elétrica",                          179.0),
    ("chaleira",            "ELETROS",          "ELE0020",  "Chaleira elétrica",                           189.0),
    ("liquidificador",      "ELETROS",          "ELE0022",  "Liquidificador 1,5L",                         319.0),
    ("depurador",           "ELETROS",          "ELE0014",  "Depurador",                                   799.0),
    ("mini_grill",          "ELETROS",          "ELE0024",  "Mini grill e sanduicheira",                   159.0),
    ("tv",                  "ELETROS",          "ELE0001",  'TV 43"',                                     1599.0),
    # ILUMINAÇÃO
    ("iluminacao",          "ILUMINAÇÃO",       "ILU0001",  "Kit iluminação",                              347.0),
    # ÁREA EXTERNA (condicional)
    ("jacuzzi",             "ÁREA EXTERNA",     "EXT0001",  "Jacuzzi circular Ø 1,80m",                  5000.0),
    ("mesa_externa",        "ÁREA EXTERNA",     "EXT0002",  "Mesa externa redonda + cadeiras",            1500.0),
]

_CADEIRAS_POR_CAP: dict[int, int] = {2: 2, 3: 3, 4: 3, 5: 4}
_TERRACO_GARDEN   = {"garden", "terraço", "terraco"}
_TERRACO_VARANDA  = {"varanda", "sacada"}


def itens_para_tipologia(
    capacidade: int,
    terraco: str,
    tipo: str,
    produtos: dict,
) -> list[LinhaMemorial]:
    """Retorna lista de LinhaMemorial para a tipologia, usando preços do catálogo
    quando disponível e defaults caso contrário."""
    t = terraco.strip().lower()
    eh_garden   = t in _TERRACO_GARDEN
    eh_varanda  = t in _TERRACO_VARANDA
    eh_pcd      = tipo.strip().lower() == "pcd"

    linhas: list[LinhaMemorial] = []
    for (role, categoria, codigo, descricao, valor_default) in _ITENS_PLUS:
        if role == "sofa_cama"    and capacidade not in (4, 5): continue
        if role == "jacuzzi"      and not eh_garden:             continue
        if role == "mesa_externa" and not eh_varanda:            continue

        qty = _CADEIRAS_POR_CAP.get(capacidade, 2) if role == "cadeira_jantar" else 1

        # Preço: catálogo sobrescreve default
        if codigo in produtos:
            p = produtos[codigo]
            valor = p.valor_unitario if isinstance(p, Produto) else p.get("valor_unitario", valor_default)
        else:
            valor = valor_default

        nome = f"{descricao} (PCD)" if (
            eh_pcd
            and "banheiro" in descricao.lower()
            and "bancada" not in descricao.lower()
        ) else descricao

        linhas.append(LinhaMemorial(categoria=categoria, item=nome,
                                    quantidade=qty, valor_unitario=valor))
    return linhas


def montar_memorial(
    tipologia: str,
    descricao: str,
    estilo: str,
    spot: str,
    linhas: list[LinhaMemorial],
) -> MemorialTipologia:
    return MemorialTipologia(
        tipologia=tipologia, descricao=descricao,
        estilo=estilo, spot=spot, linhas=linhas,
    )


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def serializar_csv(memorial: MemorialTipologia) -> str:
    out = io.StringIO()
    w = csvmodule.writer(out)

    w.writerow(["TIPOLOGIA:", memorial.tipologia, memorial.descricao])
    w.writerow(["Empreendimento:", memorial.spot])
    w.writerow(["Estilo:", memorial.estilo, "Pacote: Plus"])
    w.writerow([])
    w.writerow(["ITEM", "Quantidade", "Valor Unitário", "Valor Total"])

    cat_atual = None
    for linha in memorial.linhas:
        if linha.categoria != cat_atual:
            cat_atual = linha.categoria
            w.writerow([f" {cat_atual}", "", "", _brl(memorial.subtotais[cat_atual])])
        w.writerow([linha.item, linha.quantidade,
                    _brl(linha.valor_unitario), _brl(linha.valor_total)])

    w.writerow([])
    w.writerow(["", "", "Valor Produtos", _brl(memorial.valor_produtos)])
    w.writerow(["Taxa Decor", "R$", "", _brl(memorial.taxa_decor)])
    w.writerow(["Taxa Adm (13%)", "", "", _brl(memorial.taxa_adm)])
    w.writerow(["TOTAL GERAL", "", "", _brl(memorial.total_geral)])

    return out.getvalue()


def main() -> None:
    p = argparse.ArgumentParser(description="Gera memoriais de decor por tipologia (Plus)")
    p.add_argument("--tipologias", type=Path, required=True,
                   help="JSON com lista [{tipologia, terraco, tipo, capacidade}]")
    p.add_argument("--produtos", type=Path,
                   help="JSON de ler_catalogo.py (omitir = preços default)")
    p.add_argument("--estilo", required=True,
                   choices=["clean", "biofilico", "industrial", "bruma"])
    p.add_argument("--spot", required=True, help="Nome do empreendimento")
    args = p.parse_args()

    tipologias = json.loads(args.tipologias.read_text(encoding="utf-8"))
    produtos: dict = {}
    if args.produtos:
        raw = json.loads(args.produtos.read_text(encoding="utf-8"))
        produtos = {
            k: Produto(k, v["nome"], v["categoria"], v["valor_unitario"], v.get("unidade","un"))
            for k, v in raw.items()
        }

    memoriais = []
    for t in tipologias:
        letra    = t["tipologia"]
        descr    = f"{t['terraco']} · {t['tipo']} · Cap. {t['capacidade']}"
        linhas   = itens_para_tipologia(t["capacidade"], t["terraco"], t["tipo"], produtos)
        memorial = montar_memorial(letra, descr, args.estilo.capitalize(), args.spot, linhas)
        memoriais.append({
            "tipologia":     letra,
            "descricao":     descr,
            "total_geral":   memorial.total_geral,
            "valor_produtos":memorial.valor_produtos,
            "taxa_adm":      memorial.taxa_adm,
            "taxa_decor":    memorial.taxa_decor,
            "subtotais":     memorial.subtotais,
            "linhas": [
                {"categoria": l.categoria, "item": l.item,
                 "quantidade": l.quantidade, "valor_unitario": l.valor_unitario,
                 "valor_total": l.valor_total}
                for l in memorial.linhas
            ],
            "csv": serializar_csv(memorial),
        })

    resumo = [{"tipologia": m["tipologia"], "descricao": m["descricao"],
               "total_geral": m["total_geral"]} for m in memoriais]
    print(json.dumps({"memoriais": memoriais, "resumo": resumo},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Rodar todos os testes**

```bash
python -m pytest tests/test_montar_orcamento.py -v
```
Esperado: todos os 30+ testes passando.

- [ ] **Rodar a suite completa**

```bash
python -m pytest tests/ -q
```
Esperado: todos os testes existentes (27 da Fase 1) + novos passando.

- [ ] **Testar CLI com dados do Natal Spot**

```bash
python -c "
import json
tipologias = [
  {'tipologia':'A','terraco':'Sem','tipo':'Padrão','capacidade':2},
  {'tipologia':'B','terraco':'Sem','tipo':'Padrão','capacidade':3},
  {'tipologia':'C','terraco':'Sem','tipo':'Padrão','capacidade':5},
  {'tipologia':'D','terraco':'Sacada','tipo':'Padrão','capacidade':3},
  {'tipologia':'E','terraco':'Sacada','tipo':'Padrão','capacidade':5},
]
open('tmp/natal_tips.json','w').write(json.dumps(tipologias))
"

python skills/orcamento-decor/scripts/montar_orcamento.py \
  --tipologias tmp/natal_tips.json \
  --estilo clean \
  --spot "Natal Spot" | python -c "
import json,sys
data=json.load(sys.stdin)
for r in data['resumo']:
    print(f\"  Tip {r['tipologia']} ({r['descricao']}): R\$ {r['total_geral']:,.2f}\")
"
```

Esperado (Cap.5+Sacada deve ser maior que Cap.2+Sem):
```
  Tip A (Sem · Padrão · Cap. 2): R$ 38.XXX,XX
  Tip B (Sem · Padrão · Cap. 3): R$ 39.XXX,XX
  Tip C (Sem · Padrão · Cap. 5): R$ 43.XXX,XX
  Tip D (Sacada · Padrão · Cap. 3): R$ 40.XXX,XX
  Tip E (Sacada · Padrão · Cap. 5): R$ 44.XXX,XX
```

- [ ] **Commit**

```bash
git add skills/orcamento-decor/scripts/montar_orcamento.py tests/test_montar_orcamento.py
git commit -m "feat(orcamento): montar_orcamento.py - itens, calculos, CSV, CLI"
```

---

## Task 5: Documentação de referência

**Files:**
- Create: `skills/orcamento-decor/references/itens-por-capacidade.md`
- Create: `skills/orcamento-decor/references/catalogo-schema.md`

- [ ] **Criar `skills/orcamento-decor/references/itens-por-capacidade.md`**

```markdown
# Regras de itens por tipologia — pacote Plus

## Itens fixos (todas as tipologias)
Marcenaria completa (7 peças) · Marmoraria (2 bancadas) · Cama Queen · Puff ·
Louças e Metais (8 itens) · Eletros (9 itens) · Iluminação.

## Condicionais por Capacidade

| Condição | Item adicionado |
|---|---|
| Cap. 4 ou 5 | Sofá-cama |
| Cap. 2 | 2 cadeiras de jantar |
| Cap. 3 | 3 cadeiras de jantar |
| Cap. 4 | 3 cadeiras de jantar |
| Cap. 5 | 4 cadeiras de jantar |

## Condicionais por Terraço

| Terraço | Item adicionado |
|---|---|
| Garden ou Terraço | Jacuzzi circular Ø 1,80m |
| Varanda ou Sacada | Mesa externa redonda + cadeiras |
| Sem | Nenhum item de área externa |

## PCD
Item de banheiro ganha sufixo "(PCD)" no memorial para sinalizar especificação diferente.
Sem alteração de preço no orçamento preliminar — confirmar com fornecedor.

## Preços de referência (Plus, 2026)
Definidos em `_ITENS_PLUS` em `montar_orcamento.py`.
O catálogo real (`db002_produtos`) sempre sobrescreve esses defaults quando disponível.
Total típico por tipologia: R$ 38.000–48.000 (sem jacuzzi) / R$ 43.000–55.000 (com jacuzzi).
```

- [ ] **Criar `skills/orcamento-decor/references/catalogo-schema.md`**

```markdown
# Schema do db002_produtos

> **Preencher na primeira execução real.** Inspecione as colunas do CSV
> antes de rodar `ler_catalogo.py` em produção.

## ID do Sheet
`1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o` — aba db002_produtos (gid: 1263042396)

## Como inspecionar
Baixe via Drive (exportMimeType: text/csv) e rode:
```bash
python ler_catalogo.py --csv db002.csv 2>&1
```
Se falhar, o erro lista as colunas disponíveis. Se passar, documente aqui.

## Colunas esperadas (a confirmar)
- `codigo` (ou variante) → código do produto (ex: MRC0002, MOB0001)
- `nome` (ou variante) → descrição do item
- `categoria` (ou variante) → MARCENARIA | MOBILIÁRIO | ELETROS | etc.
- `valor_unitario` (ou variante) → preço em reais (ex: 3300.00 ou "R$ 3.300,00")
- `unidade` (opcional) → un, m², kit

## Mapeamento manual (se auto-detecção falhar)
```bash
python ler_catalogo.py --csv db002.csv \
  --col-codigo <nome_real_da_coluna> \
  --col-nome <nome_real_da_coluna> \
  --col-categoria <nome_real_da_coluna> \
  --col-valor_unitario <nome_real_da_coluna>
```
```

- [ ] **Commit**

```bash
git add skills/orcamento-decor/references/
git commit -m "docs(orcamento): referencias itens-por-capacidade e catalogo-schema"
```

---

## Task 6: SKILL.md

**Files:**
- Create: `skills/orcamento-decor/SKILL.md`

- [ ] **Criar `skills/orcamento-decor/SKILL.md`**

```markdown
---
name: orcamento-decor
description: Gera o orçamento preliminar de decor (memorial descritivo, pacote Plus) por tipologia de um Spot, usando preços do catálogo real no Drive. Ativa com "gera o orçamento do <Spot>", "memorial de decor do <Spot>", "orçamento preliminar", /orcamento-decor.
---

# Skill: orcamento-decor

Gera memorial descritivo de decor por tipologia (pacote Plus fixo, estilo a escolher).
**NÃO modifica a skill tabela-tipologias nem seus arquivos.**

## Quando usar
"gera o orçamento do <Spot>", "memorial de decor do <Spot>", "orçamento preliminar", `/orcamento-decor`.

## Procedimento

### 1. Identificar Spot e estilo

Leia `dashboard/data/tipologias.js`. Ache o spot pelo nome no `index`.
- Se o entry já tiver campo `estilo`: use-o.
- Se não tiver: pergunte → "Qual o estilo deste Spot? (1) Clean  (2) Biofílico  (3) Industrial  (4) Bruma"
- Salve como `ESTILO` (ex: `clean`, `biofilico`, `industrial`, `bruma`).

Guarde também: `SPOT_NAME`, `SLUG`, `TIPOLOGIAS_DRIVE_URL` (campo `drive_url`).

### 2. Baixar catálogo do Drive

```
GOOGLEDRIVE_DOWNLOAD_FILE
  fileId: 1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o
  exportMimeType: text/csv
```
Salve em `tmp/db002.csv`. Se falhar por timeout/permissão: pule o passo 3 (usará preços default).

### 3. Parsear catálogo

```bash
python skills/orcamento-decor/scripts/ler_catalogo.py --csv tmp/db002.csv > tmp/produtos.json
```

Se o script falhar com "Colunas não encontradas":
- O erro mostra as colunas disponíveis
- Consulte `skills/orcamento-decor/references/catalogo-schema.md`
- Chame novamente com `--col-<campo> <nome_real>`
- Documente o schema correto em `catalogo-schema.md` e faça commit

### 4. Preparar tipologias.json

Extraia de `dashboard/data/tipologias.js` → `spots["SLUG"].tipologias` e salve em `tmp/tipologias_spot.json`.
Formato esperado:
```json
[{"tipologia":"A","terraco":"Sem","tipo":"Padrão","capacidade":2}, ...]
```

### 5. Gerar memoriais

```bash
python skills/orcamento-decor/scripts/montar_orcamento.py \
  --tipologias tmp/tipologias_spot.json \
  --produtos tmp/produtos.json \
  --estilo ESTILO \
  --spot "SPOT_NAME" > tmp/memoriais.json
```
(Se pulou o passo 3, omita `--produtos`.)

### 6. Criar Sheets de orçamento no Drive

Encontre a pasta `02 - Imagens` do Spot (mesmo caminho da skill tabela-tipologias:
`Spot / 02 - Projetos / 05 - Projeto Arquitetônico / 10 - Projeto de Interiores / 02 - Imagens`).

Para CADA memorial em `tmp/memoriais.json`:
```
GOOGLEDRIVE_CREATE_FILE_FROM_TEXT
  title: "Orçamento Decor - SPOT_NAME - Tipologia LETRA (ESTILO Plus)"
  text_content: <campo "csv" do memorial>
  content_mime_type: text/csv
  parent_id: <id da pasta 02 - Imagens>
```
O Drive converte o CSV em Sheet editável. Guarde o link retornado.

### 7. Criar Sheet tipologias + custo

Baixe o CSV do Sheet de tipologias original via Drive (use `drive_url` do spot):
```
GOOGLEDRIVE_DOWNLOAD_FILE fileId: <id> exportMimeType: text/csv
```

Adicione coluna `CUSTO ESTIMADO DECOR (Plus ESTILO)` com o `total_geral` de cada tipologia.
Crie novo Sheet:
```
GOOGLEDRIVE_CREATE_FILE_FROM_TEXT
  title: "SPOT_NAME - Tipologias + Custo Plus ESTILO"
  text_content: <CSV original com coluna extra>
  content_mime_type: text/csv
  parent_id: <id da pasta 02 - Imagens>
```

### 8. Atualizar tipologias.js

Se o spot não tinha `estilo`, adicione ao entry do index:
```javascript
estilo: "ESTILO",
orcamento_url: "<link do Sheet tipologias+custo>"
```
Faça commit:
```bash
git add dashboard/data/tipologias.js
git commit -m "feat(orcamento): estilo e orcamento_url do SPOT_NAME"
```

### 9. Apresentar resultado

Mostre:
```
✅ Orçamento gerado — SPOT_NAME (ESTILO · Plus)

Tipologia | Descrição               | Custo estimado
A         | Sem · Padrão · Cap. 2   | R$ XX.XXX,XX
B         | Garden · Padrão · Cap. 4| R$ XX.XXX,XX
...

Sheets criados:
- [Tipologia A] <link>
- [Tipologia B] <link>
- ...
- [Tipologias + Custo] <link>

⚠ Preços de referência (Plus 2026). Confirmar com catálogo atualizado.
```

## IDs do Drive

| Recurso | ID |
|---|---|
| Catálogo principal (db002_produtos) | `1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o` |
| Marcenaria por estilo | `1VnEZ-2UscCx03cwEGEDVA9vbfaUw4Y04wiM_lh9YRYI` |
| Pasta raiz estilos | `1uEBBTJlSUpOh2WxM1GRbx1e932xqI_dy` |
| Pasta estilo CLEAN | `17Nh0A_EsLt1gvwdB-9kcMtTVKkJSsX5O` |
| Pasta estilo BIOFÍLICO | `10HKb-ckaIp_x81LXBvEGevEwIAcmD46H` |
| Pasta estilo INDUSTRIAL | `1XFt6ucRgmmq1PGn4vNxv3tiHuVfmT5Jd` |
| Pasta estilo BRUMA | `19HSW3nsiNcpY5RZNZO4NRguHtXAGgq98` |
```

- [ ] **Commit**

```bash
git add skills/orcamento-decor/SKILL.md
git commit -m "feat(orcamento): SKILL.md com fluxo completo (Fase 2)"
```

---

## Task 7: Instalar skill globalmente + validação final

**Files:**
- Copia `skills/orcamento-decor/` → `C:\Users\Seazone\Claude\.claude\skills\orcamento-decor\`

- [ ] **Rodar suite completa de testes para confirmar que nada quebrou**

```bash
python -m pytest tests/ -q
```
Esperado: todos os testes passando (27 Fase 1 + novos Fase 2). Nenhum erro.

- [ ] **Instalar a skill globalmente**

```powershell
$src = "C:\Users\Seazone\Claude\seazone\hackathon-investimentos\skills\orcamento-decor"
$dst = "C:\Users\Seazone\Claude\.claude\skills\orcamento-decor"
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item $src $dst -Recurse
Write-Host "Instalado em $dst"
```

- [ ] **Commit final**

```bash
git add .
git status  # confirmar que só arquivos novos da skill foram adicionados
git commit -m "feat(fase2): skill orcamento-decor instalada e testada"
```

- [ ] **Push para o GitHub**

```bash
git push origin master
```

---

## Validação de referência pós-implementação

Após a implementação, rodar a skill com Novo Campeche II (12 tipologias / 49 unidades) e verificar:
1. Total por tipologia está no range R$ 35.000–55.000 (razoável para Plus)
2. Tipologias com Garden/Terraço têm jacuzzi (+ ~R$ 5.000 no total)
3. Tipologias Cap. 4 e 5 têm sofá-cama (+ ~R$ 4.373)
4. Sheet de tipologias+custo bate com os 12 totais individuais
