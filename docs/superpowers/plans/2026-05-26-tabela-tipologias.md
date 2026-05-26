# Skill `tabela-tipologias` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir a skill `tabela-tipologias`, que puxa o anteprojeto LANÇAMENTOS de um Spot no Drive, classifica cada unidade por pavimento e agrupa em tipologias, entregando um Google Sheet editável + resumo executivo.

**Architecture:** Skill do Claude Code (SKILL.md + references) onde o **Claude faz a parte analítica em runtime** (navegar Drive, ler PDF/xlsx, classificar unidades). A parte **determinística** (agrupar unidades classificadas em tipologias, validar totais, gerar CSV) fica num helper Python testável (`montar_tabela.py`), guiado por TDD. O Google Sheet é criado via MCP de Sheets em runtime.

**Tech Stack:** Python 3.12 (stdlib `csv`, `json`; binário `python`, NÃO `python3`), pytest (dev), MCP Google Drive + Google Sheets. Sem openpyxl (saída é Google Sheet + CSV).

**Spec:** `docs/superpowers/specs/2026-05-26-tabela-tipologias-design.md`

---

## File Structure

```
hackathon-investimentos/
├── skills/tabela-tipologias/
│   ├── SKILL.md                       # procedimento de runtime (Tarefa 6)
│   ├── references/
│   │   ├── classificacao-spot.md      # Matriz Capacidade, Tipos, Áreas externas (Tarefa 5)
│   │   └── drive-navegacao.md         # convenção de pastas + regra LANÇAMENTOS (Tarefa 5)
│   └── scripts/
│       └── montar_tabela.py           # agrupar + validar + CSV (Tarefas 2-4)
└── tests/
    ├── conftest.py                    # fixture de unidades do Natal (Tarefa 1)
    └── test_montar_tabela.py          # TDD do helper (Tarefas 2-4)
```

**Contrato de dados — unidade classificada (JSON):**
```json
{
  "unidade": "101",
  "pavimento": 1,
  "terraco": "Sem",
  "tipo": "Padrão",
  "capacidade": 2,
  "area_util": 14.33,
  "area_unidade": 18.50
}
```
`terraco` ∈ {Sem, Sacada, Garden, Terraço}. `tipo` ∈ {Padrão, PCD, Mezanino, Único}. `capacidade` ∈ {2,3,4,5} (previsão).

---

### Task 1: Scaffold + fixture do Natal

**Files:**
- Create: `skills/tabela-tipologias/scripts/montar_tabela.py` (vazio com docstring)
- Create: `tests/conftest.py`
- Test: `tests/test_montar_tabela.py` (stub)

- [ ] **Step 1: Instalar pytest (uma vez)**

Run: `python -m pip install pytest`
Expected: termina com "Successfully installed pytest-..." (ou "already satisfied").

- [ ] **Step 2: Criar diretórios e arquivo do helper com docstring**

Create `skills/tabela-tipologias/scripts/montar_tabela.py`:
```python
"""Agrupa unidades classificadas em tipologias, valida totais e gera CSV.

Uso (runtime da skill):
    python montar_tabela.py --total 96 < unidades.json

Entrada: JSON (stdin) = lista de unidades classificadas.
Saída: JSON (stdout) = {"tipologias": [...], "validacao": {...}, "csv": "..."}.
"""
import csv
import io
import json
import sys
from collections import defaultdict
```

- [ ] **Step 3: Criar fixture com os dados reais do Natal Spot**

Create `tests/conftest.py`:
```python
import pytest

TERRACO_SEM, TERRACO_SACADA = "Sem", "Sacada"
TIPO_PADRAO = "Padrão"


def _unidades(n, terraco, tipo, capacidade, area_util, area_unidade, start=1):
    return [
        {
            "unidade": str(start + i),
            "pavimento": (start + i) // 100,
            "terraco": terraco,
            "tipo": tipo,
            "capacidade": capacidade,
            "area_util": area_util,
            "area_unidade": area_unidade,
        }
        for i in range(n)
    ]


@pytest.fixture
def unidades_natal():
    """Natal Spot: 96 unidades, 5 tipologias (verdade conhecida do anteprojeto)."""
    return (
        _unidades(74, TERRACO_SEM, TIPO_PADRAO, 2, 14.33, 18.50, start=101)
        + _unidades(10, TERRACO_SEM, TIPO_PADRAO, 5, 19.94, 24.00, start=201)
        + _unidades(10, TERRACO_SEM, TIPO_PADRAO, 3, 15.18, 19.00, start=301)
        + _unidades(1, TERRACO_SACADA, TIPO_PADRAO, 5, 15.18, 22.00, start=407)
        + _unidades(1, TERRACO_SACADA, TIPO_PADRAO, 3, 15.10, 21.50, start=408)
    )
```

- [ ] **Step 4: Stub do teste e rodar a coleta**

Create `tests/test_montar_tabela.py`:
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tabela-tipologias" / "scripts"))


def test_fixture_tem_96_unidades(unidades_natal):
    assert len(unidades_natal) == 96
```

Run: `python -m pytest tests/test_montar_tabela.py -v`
Expected: PASS (1 passed).

- [ ] **Step 5: Commit**

```bash
git add skills/tabela-tipologias/scripts/montar_tabela.py tests/conftest.py tests/test_montar_tabela.py
git commit -m "chore: scaffold skill tabela-tipologias + fixture Natal"
```

---

### Task 2: `agrupar()` — agrupar unidades em tipologias

**Files:**
- Modify: `skills/tabela-tipologias/scripts/montar_tabela.py`
- Test: `tests/test_montar_tabela.py`

- [ ] **Step 1: Escrever os testes que falham**

Append to `tests/test_montar_tabela.py`:
```python
from montar_tabela import agrupar


def test_agrupar_natal_gera_5_tipologias(unidades_natal):
    tipologias, avisos = agrupar(unidades_natal)
    assert len(tipologias) == 5


def test_agrupar_atribui_letras_sequenciais(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    assert [t["tipologia"] for t in tipologias] == ["A", "B", "C", "D", "E"]


def test_agrupar_maior_grupo_primeiro(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    assert tipologias[0]["quantidade"] == 74
    assert tipologias[0]["capacidade"] == 2
    assert tipologias[0]["terraco"] == "Sem"


def test_agrupar_quantidades_e_atributos(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    chave = {(t["terraco"], t["capacidade"]): t["quantidade"] for t in tipologias}
    assert chave[("Sem", 2)] == 74
    assert chave[("Sem", 5)] == 10
    assert chave[("Sem", 3)] == 10
    assert chave[("Sacada", 5)] == 1
    assert chave[("Sacada", 3)] == 1


def test_agrupar_lista_unidades(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    t_a = next(t for t in tipologias if t["tipologia"] == "A")
    assert len(t_a["unidades"]) == 74
    assert "101" in t_a["unidades"]


def test_agrupar_avisa_quando_area_diverge_alem_da_tolerancia():
    unidades = [
        {"unidade": "1", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.0, "area_unidade": 18.0},
        {"unidade": "2", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 20.0, "area_unidade": 24.0},
    ]
    tipologias, avisos = agrupar(unidades, tolerancia_m2=1.0)
    assert len(tipologias) == 1
    assert any("área" in a.lower() or "area" in a.lower() for a in avisos)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_montar_tabela.py -v`
Expected: FAIL com `ImportError: cannot import name 'agrupar'`.

- [ ] **Step 3: Implementar `agrupar()`**

Append to `montar_tabela.py`:
```python
_TERRACO_ORDEM = {"Sem": 0, "Sacada": 1, "Varanda": 2, "Garden": 3, "Terraço": 4}


def agrupar(unidades, tolerancia_m2=1.0):
    """Agrupa unidades por (terraco, tipo, capacidade) em tipologias A, B, C...

    Ordena por quantidade desc, depois terraco, depois capacidade asc.
    Sinaliza em `avisos` grupos cuja área útil varia além de `tolerancia_m2`.
    Retorna (lista_de_tipologias, lista_de_avisos).
    """
    grupos = defaultdict(list)
    for u in unidades:
        grupos[(u["terraco"], u["tipo"], u["capacidade"])].append(u)

    itens = []
    for (terraco, tipo, capacidade), us in grupos.items():
        areas_uteis = [u["area_util"] for u in us]
        areas_unid = [u["area_unidade"] for u in us]
        itens.append({
            "terraco": terraco,
            "tipo": tipo,
            "capacidade": capacidade,
            "quantidade": len(us),
            "unidades": [u["unidade"] for u in us],
            "area_util_min": min(areas_uteis),
            "area_util_max": max(areas_uteis),
            "area_unidade_min": min(areas_unid),
            "area_unidade_max": max(areas_unid),
        })

    itens.sort(key=lambda t: (
        -t["quantidade"],
        _TERRACO_ORDEM.get(t["terraco"], 99),
        t["capacidade"],
    ))

    avisos = []
    for i, t in enumerate(itens):
        t["tipologia"] = chr(ord("A") + i)
        if t["area_util_max"] - t["area_util_min"] > tolerancia_m2:
            avisos.append(
                f"Tipologia {t['tipologia']}: área útil varia de "
                f"{t['area_util_min']:.2f} a {t['area_util_max']:.2f} m² "
                f"(> {tolerancia_m2} m²) — conferir se são o mesmo layout."
            )
    return itens, avisos
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_montar_tabela.py -v`
Expected: PASS (todos os testes de `agrupar`).

- [ ] **Step 5: Commit**

```bash
git add skills/tabela-tipologias/scripts/montar_tabela.py tests/test_montar_tabela.py
git commit -m "feat: agrupar unidades em tipologias com tolerancia de area"
```

---

### Task 3: `validar()` — conferir soma das quantidades

**Files:**
- Modify: `skills/tabela-tipologias/scripts/montar_tabela.py`
- Test: `tests/test_montar_tabela.py`

- [ ] **Step 1: Escrever os testes que falham**

Append to `tests/test_montar_tabela.py`:
```python
from montar_tabela import validar


def test_validar_ok_quando_soma_bate(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    v = validar(tipologias, total_declarado=96)
    assert v["ok"] is True
    assert v["soma"] == 96
    assert v["diff"] == 0


def test_validar_falha_quando_soma_nao_bate(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    v = validar(tipologias, total_declarado=100)
    assert v["ok"] is False
    assert v["soma"] == 96
    assert v["diff"] == -4
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_montar_tabela.py -k validar -v`
Expected: FAIL com `ImportError: cannot import name 'validar'`.

- [ ] **Step 3: Implementar `validar()`**

Append to `montar_tabela.py`:
```python
def validar(tipologias, total_declarado):
    """Confere se a soma das quantidades bate com o total declarado no anteprojeto."""
    soma = sum(t["quantidade"] for t in tipologias)
    diff = soma - total_declarado
    return {
        "ok": diff == 0,
        "soma": soma,
        "total_declarado": total_declarado,
        "diff": diff,
    }
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python -m pytest tests/test_montar_tabela.py -k validar -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/tabela-tipologias/scripts/montar_tabela.py tests/test_montar_tabela.py
git commit -m "feat: validar soma das quantidades vs total declarado"
```

---

### Task 4: `to_csv()` + CLI `main()`

**Files:**
- Modify: `skills/tabela-tipologias/scripts/montar_tabela.py`
- Test: `tests/test_montar_tabela.py`

- [ ] **Step 1: Escrever os testes que falham**

Append to `tests/test_montar_tabela.py`:
```python
from montar_tabela import to_csv


def test_to_csv_tem_cabecalho_e_rodape(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    csv_txt = to_csv(tipologias, total_unidades=96)
    linhas = csv_txt.strip().splitlines()
    assert linhas[0] == (
        "TIPOLOGIA,N DAS UNIDADES,TERRAÇO,TIPO,QUANTIDADE,"
        "CAPACIDADE (previsão),ÁREA ÚTIL (m²),ÁREA DA UNIDADE (m²)"
    )
    assert "Total de Tipologias,5" in csv_txt
    assert "Total de Unidades,96" in csv_txt


def test_to_csv_capacidade_marcada_como_previsao(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    csv_txt = to_csv(tipologias, total_unidades=96)
    assert "previsão" in csv_txt.lower()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_montar_tabela.py -k to_csv -v`
Expected: FAIL com `ImportError: cannot import name 'to_csv'`.

- [ ] **Step 3: Implementar `to_csv()` e `main()`**

Append to `montar_tabela.py`:
```python
def _fmt_area(mn, mx):
    return f"{mn:.2f}" if abs(mx - mn) < 0.01 else f"{mn:.2f}–{mx:.2f}"


def to_csv(tipologias, total_unidades):
    """Gera o CSV da tabela de tipologias (cabeçalho + linhas + rodapé)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "TIPOLOGIA", "N DAS UNIDADES", "TERRAÇO", "TIPO", "QUANTIDADE",
        "CAPACIDADE (previsão)", "ÁREA ÚTIL (m²)", "ÁREA DA UNIDADE (m²)",
    ])
    for t in tipologias:
        w.writerow([
            t["tipologia"],
            ", ".join(t["unidades"]),
            t["terraco"],
            t["tipo"],
            t["quantidade"],
            t["capacidade"],
            _fmt_area(t["area_util_min"], t["area_util_max"]),
            _fmt_area(t["area_unidade_min"], t["area_unidade_max"]),
        ])
    w.writerow([])
    w.writerow(["Total de Tipologias", len(tipologias)])
    w.writerow(["Total de Unidades", total_unidades])
    return buf.getvalue()


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="Monta a tabela de tipologias.")
    p.add_argument("--total", type=int, required=True,
                   help="Total de unidades declarado no anteprojeto.")
    p.add_argument("--tolerancia", type=float, default=1.0,
                   help="Tolerância de variação de área útil (m²) dentro de uma tipologia.")
    args = p.parse_args(argv)

    unidades = json.load(sys.stdin)
    tipologias, avisos = agrupar(unidades, tolerancia_m2=args.tolerancia)
    validacao = validar(tipologias, total_declarado=args.total)
    csv_txt = to_csv(tipologias, total_unidades=args.total)
    json.dump(
        {"tipologias": tipologias, "validacao": validacao,
         "avisos": avisos, "csv": csv_txt},
        sys.stdout, ensure_ascii=False, indent=2,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Rodar e ver passar (e a suíte toda)**

Run: `python -m pytest tests/ -v`
Expected: PASS (todos).

- [ ] **Step 5: Smoke test do CLI com dado real do Natal**

Run:
```bash
python - <<'PY' | python skills/tabela-tipologias/scripts/montar_tabela.py --total 96
import json,sys
def u(n,terraco,cap,au,aun,start):
    return [{"unidade":str(start+i),"pavimento":(start+i)//100,"terraco":terraco,
             "tipo":"Padrão","capacidade":cap,"area_util":au,"area_unidade":aun} for i in range(n)]
data=u(74,"Sem",2,14.33,18.5,101)+u(10,"Sem",5,19.94,24,201)+u(10,"Sem",3,15.18,19,301)+u(1,"Sacada",5,15.18,22,407)+u(1,"Sacada",3,15.10,21.5,408)
json.dump(data,sys.stdout)
PY
```
Expected: JSON com `"validacao": {"ok": true, "soma": 96, ...}` e 5 tipologias no `csv`.

- [ ] **Step 6: Commit**

```bash
git add skills/tabela-tipologias/scripts/montar_tabela.py tests/test_montar_tabela.py
git commit -m "feat: gerar CSV da tabela de tipologias + CLI"
```

---

### Task 5: Documentos de referência da skill

**Files:**
- Create: `skills/tabela-tipologias/references/classificacao-spot.md`
- Create: `skills/tabela-tipologias/references/drive-navegacao.md`

- [ ] **Step 1: Criar `classificacao-spot.md`**

Create with o conteúdo de classificação (extraído do projeto `mapeamento-completo-de-mobilirio--unidade-spot`):
```markdown
# Classificação de tipologias Spot

Cada unidade é classificada por **Terraço + Tipo construtivo + Capacidade**.

## Terraço / Área externa
Sem · Sacada · Varanda · Garden · Terraço. (Garden/Terraço = área externa ampla;
Sacada/Varanda = compacta.)

## Tipo construtivo
Padrão · PCD (porta de correr, raio de giro Ø 1,50m, acesso bilateral à cama) ·
Mezanino (2 pisos) · Único.

## Capacidade (PREVISÃO — confirmar com layout final)
Derivada de área útil + terraço + programa de mobiliário:
- **Base (cap. 2):** Cama Queen + cabeceira + copa linear + bancada + arara +
  vassoureiro + TV. 60cm de circulação ao redor da cama; 20cm cama↔janela.
- **Cama auxiliar** (0,67×1,90m) cabe ao lado da Queen → habilita **cap. 3 e 5**.
- **Sofá-cama** (aberto 1,62×2,00m = leito) → habilita **cap. 4 e 5**.
- **Mesa redonda / jacuzzi externos** → quando há varanda/garden/terraço.

Matriz resumida:
| Capacidade | Cama auxiliar | Sofá-cama |
|-----------|---------------|-----------|
| 2         | não           | não       |
| 3         | sim           | não       |
| 4         | não           | sim       |
| 5         | sim           | sim       |

## Agrupamento em tipologias
Unidades com o **mesmo layout/desenho** + Terraço + Tipo + Capacidade são a
mesma tipologia, **mesmo que o m² difira por pouco** (tolerância ~1 m²).
Diferença grande de m² (layout distinto) separa. Casos de fronteira → sinalizar.
```

- [ ] **Step 2: Criar `drive-navegacao.md`**

Create:
```markdown
# Navegação no Drive até o anteprojeto

Pasta raiz dos projetos: `1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF`

Caminho por empreendimento:
```
[Spot "1.X - [código] Nome Spot"]
  / 02 - Projetos
    / 05 - Projeto Arquitetônico
      / 03 - Anteprojeto
        / [última versão LANÇAMENTOS]
          / LANÇAMENTO_AP_<nome>_V0X.pdf   (+ ANÁLISE_..._V0X.xlsx)
```

## Regra rígida de versão
Dentro de `03 - Anteprojeto`, escolher a última pasta/arquivo que contém
**"LANÇAMENTO(S)"** no nome. **NUNCA** usar "COMPATIBILIZADO INTERIORES".
Número de versão maior NÃO implica correta — filtrar por LANÇAMENTOS primeiro,
depois pegar a mais recente.

## Fontes de dados (ordem de preferência)
1. `ANÁLISE_LANÇAMENTO_..._V0X.xlsx` — dados estruturados (unidade → área → terraço).
2. Página de QUADRO DE ÁREAS / QUADRO DE UNIDADES dentro do PDF.
3. Plantas de pavimento (leitura multimodal página a página) — menor confiança.

## Ferramentas MCP
- `GOOGLEDRIVE_FIND_FILE` (listar/buscar por `folder_id`).
- `GOOGLEDRIVE_DOWNLOAD_FILE` (baixar PDF/xlsx; retorna URL temporária — baixar com curl).
```

- [ ] **Step 3: Commit**

```bash
git add skills/tabela-tipologias/references/
git commit -m "docs: referencias de classificacao e navegacao Drive da skill"
```

---

### Task 6: SKILL.md — procedimento de runtime

**Files:**
- Create: `skills/tabela-tipologias/SKILL.md`

- [ ] **Step 1: Escrever o SKILL.md**

Create `skills/tabela-tipologias/SKILL.md`:
```markdown
---
name: tabela-tipologias
description: Use quando a Raquel (ou alguém de Lançamentos/Decor) pedir para montar/gerar a tabela de tipologias de um empreendimento Spot a partir do anteprojeto. Puxa o anteprojeto LANÇAMENTOS do Drive, classifica cada unidade por pavimento (Terraço + Tipo + Capacidade-previsão) e agrupa em tipologias, entregando um Google Sheet editável + resumo executivo. Ativa com "tabela de tipologias", "monta as tipologias do <Spot>", "quadro de tipologias".
---

# Skill: tabela-tipologias

Gera a tabela de tipologias de um Spot a partir do anteprojeto no Drive.

## Quando usar
Pedidos como "monta a tabela de tipologias do Natal Spot", "tipologias do <Spot>".

## Procedimento

### 1. Localizar o anteprojeto
Leia `references/drive-navegacao.md`. A partir do nome do Spot:
1. `GOOGLEDRIVE_FIND_FILE` na raiz `1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF` → ache a pasta do Spot.
2. Desça `02 - Projetos` → `05 - Projeto Arquitetônico` → `03 - Anteprojeto`.
3. Escolha a última versão **LANÇAMENTOS** (NUNCA COMPATIBILIZADO INTERIORES).
4. Pegue o `ANÁLISE_..._V0X.xlsx` (preferência) e/ou o `LANÇAMENTO_AP_..._V0X.pdf`.

### 2. Levantar as unidades (todos os pavimentos)
Preferir o `ANÁLISE.xlsx` (baixar via `GOOGLEDRIVE_DOWNLOAD_FILE` → curl → ler).
Senão, achar a página de QUADRO DE ÁREAS no PDF (varrer texto antes de ler imagem).
Enumere TODAS as unidades com: número, pavimento, área útil, área da unidade, terraço.

### 3. Classificar cada unidade
Leia `references/classificacao-spot.md`. Para cada unidade derive:
`terraco`, `tipo`, `capacidade` (PREVISÃO), `area_util`, `area_unidade`.
Monte uma lista JSON no contrato do helper.

### 4. Agrupar, validar e gerar CSV
Rode o helper:
`python skills/tabela-tipologias/scripts/montar_tabela.py --total <TOTAL_DECLARADO> < unidades.json`
Ele retorna `tipologias`, `validacao` (soma vs total), `avisos` e `csv`.
**Se `validacao.ok == false`, NÃO entregue como certo — destaque a divergência.**

### 5. Entregar
1. Salve o CSV em `docs/tipologias_<spot>.csv` (snapshot versionável).
2. Crie um **novo** Google Sheet no Drive (`GOOGLESHEETS_CREATE_GOOGLE_SHEET1` + escrita
   de valores). NÃO sobrescreva planilhas existentes. Devolva o link.
3. Coloque na planilha a nota fixa de capacidade:
   "⚠️ Capacidade é previsão baseada em área útil + programa — confirmar/editar
   quando o layout final estiver pronto."
4. Escreva um **resumo executivo** (chat + opcional no Sheet): total de tipologias/
   unidades, resultado da validação, `avisos` de baixa confiança/fronteira de área,
   premissas usadas na previsão de capacidade.

## Validação de referência
Natal Spot deve dar **5 tipologias / 96 unidades** (A=74/cap2, B=10/cap5, C=10/cap3,
D=1/cap5 sacada, E=1/cap3 sacada).
```

- [ ] **Step 2: Verificar que o helper roda a partir do caminho do SKILL.md**

Run: `python skills/tabela-tipologias/scripts/montar_tabela.py --help`
Expected: imprime o help do argparse (sem erro de import).

- [ ] **Step 3: Commit**

```bash
git add skills/tabela-tipologias/SKILL.md
git commit -m "feat: SKILL.md do tabela-tipologias (procedimento de runtime)"
```

---

### Task 7: Dry-run real no Natal Spot + registro de erros

**Files:**
- Create: `docs/tipologias_natal-spot.csv` (gerado)
- Modify: `lessons.md` (se aparecerem erros novos)

- [ ] **Step 1: Executar a skill ponta a ponta no Natal Spot**

Seguindo o `SKILL.md`: localizar o anteprojeto LANÇAMENTOS do Natal Spot no Drive,
levantar as 96 unidades, classificar, rodar o helper com `--total 96`.

- [ ] **Step 2: Conferir contra a verdade conhecida**

Expected: `validacao.ok == true`, 5 tipologias, totais batendo
(A=74/cap2, B=10/cap5, C=10/cap3, D=1/cap5 sacada, E=1/cap3 sacada).
Se divergir, investigar a fonte (xlsx vs PDF) e registrar em `lessons.md`.

- [ ] **Step 3: Gerar o Google Sheet e salvar o snapshot CSV**

Crie o Google Sheet (link de volta) e salve `docs/tipologias_natal-spot.csv`.

- [ ] **Step 4: Commit**

```bash
git add docs/tipologias_natal-spot.csv lessons.md
git commit -m "test: dry-run da skill no Natal Spot (5 tipologias / 96 un)"
```

---

## Notas de execução
- Use sempre o binário `python` (NÃO `python3`, que é o alias quebrado do Windows Store).
- Escrita no Drive/Sheets só para **criar** planilha nova — nunca sobrescrever arquivos
  de produção (regra do workspace Seazone).
- Fase 2 (fora deste plano): orçamento preliminar do decor puxando do catálogo, em
  cima da tabela de tipologias gerada aqui.
