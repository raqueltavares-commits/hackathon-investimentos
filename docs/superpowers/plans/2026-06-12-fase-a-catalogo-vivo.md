# Fase A — Catálogo vivo (Supabase) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trocar a fonte de preço da skill `orcamento-decor` do CSV do Drive para leitura ao vivo do catálogo no Supabase, mantendo `montar_orcamento.py` intacto.

**Architecture:** Um de-para versionado (código-de-item da skill → `produto.codigo` da base) + um novo leitor `fetch_catalogo.py` que extrai a anon key do bundle de produção, consulta a tabela `produto` via PostgREST e devolve um `produtos.json` no MESMO formato que `ler_catalogo.py` produzia. Como `montar_orcamento.py` busca preço por código de item, nada downstream muda.

**Tech Stack:** Python 3.12 stdlib (`urllib`, `json`, `re`, `argparse`), pytest. Sem dependências novas.

---

## Constantes e dados de referência

- `SITE_URL = "https://seazone-decor-interno.seazone.properties"`
- `SUPABASE_URL = "https://cjbsotszriddpadznhvk.supabase.co"`
- De-para (código-item da skill → `produto.codigo` da base), 33 itens, escolhidos pelo produto mais usado nos memoriais Plus reais:

```
MRC0002→73   MRC0011→78   MRC0038→148  MRC0028→1237 MRC0022→181
MRC0020→113  MRC0022b→138 MRM0007→896  MRM0016→567  MOB0001→190
MOB0003→333  MOB0004→206  MOB0005→200  LEM0007→584  LEM0018→600
LEM0020→602  LEM0012→590  VDR0004→570  LEM0027→606  LEM0013→582
LEM0001→572  ELE0006→449  ELE0003→702  ELE0007→706  ELE0019→708
ELE0020→709  ELE0022→711  ELE0014→707  ELE0024→713  ELE0001→452
ILU0001→799  EXT0001→1554 EXT0002→1235
```

## File Structure

- Create: `skills/orcamento-decor/references/depara-catalogo.json` — mapa código-item → `produto.codigo` (flat, 33 entradas).
- Create: `skills/orcamento-decor/scripts/fetch_catalogo.py` — funções puras (extração de key/bundle, normalização, parse) + wrapper de rede + `main()`.
- Create: `tests/test_fetch_catalogo.py` — testes das funções puras + cobertura do de-para.
- Create: `tests/fixtures/produto_api_sample.json` — resposta PostgREST de exemplo (com double-encoding pra testar normalização).
- Modify: `skills/orcamento-decor/SKILL.md` — passos 2–3 passam a chamar `fetch_catalogo.py`.
- Modify: `skills/orcamento-decor/references/catalogo-schema.md` — documenta a nova fonte (Supabase) e o de-para.

`ler_catalogo.py` permanece (fallback offline a partir de CSV), mas deixa de ser o caminho padrão.

---

### Task 1: De-para versionado + guarda de cobertura

**Files:**
- Create: `skills/orcamento-decor/references/depara-catalogo.json`
- Test: `tests/test_fetch_catalogo.py`

- [ ] **Step 1: Criar o arquivo de de-para**

Create `skills/orcamento-decor/references/depara-catalogo.json`:

```json
{
  "MRC0002": 73,
  "MRC0011": 78,
  "MRC0038": 148,
  "MRC0028": 1237,
  "MRC0022": 181,
  "MRC0020": 113,
  "MRC0022b": 138,
  "MRM0007": 896,
  "MRM0016": 567,
  "MOB0001": 190,
  "MOB0003": 333,
  "MOB0004": 206,
  "MOB0005": 200,
  "LEM0007": 584,
  "LEM0018": 600,
  "LEM0020": 602,
  "LEM0012": 590,
  "VDR0004": 570,
  "LEM0027": 606,
  "LEM0013": 582,
  "LEM0001": 572,
  "ELE0006": 449,
  "ELE0003": 702,
  "ELE0007": 706,
  "ELE0019": 708,
  "ELE0020": 709,
  "ELE0022": 711,
  "ELE0014": 707,
  "ELE0024": 713,
  "ELE0001": 452,
  "ILU0001": 799,
  "EXT0001": 1554,
  "EXT0002": 1235
}
```

- [ ] **Step 2: Escrever o teste de cobertura do de-para (falha)**

Create `tests/test_fetch_catalogo.py`:

```python
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "skills/orcamento-decor/scripts"
REFS = Path(__file__).parent.parent / "skills/orcamento-decor/references"
sys.path.insert(0, str(SCRIPTS))

from montar_orcamento import _ITENS_PLUS


def test_depara_cobre_todos_os_itens_plus():
    depara = json.loads((REFS / "depara-catalogo.json").read_text(encoding="utf-8"))
    codigos_itens = {codigo for (_role, _cat, codigo, _desc, _val) in _ITENS_PLUS}
    assert codigos_itens.issubset(depara.keys()), (
        f"Faltam no de-para: {codigos_itens - depara.keys()}"
    )


def test_depara_aponta_para_codigos_inteiros():
    depara = json.loads((REFS / "depara-catalogo.json").read_text(encoding="utf-8"))
    assert all(isinstance(v, int) for v in depara.values())
```

- [ ] **Step 3: Rodar o teste e verificar que passa**

Run: `python -m pytest tests/test_fetch_catalogo.py -v`
Expected: PASS (2 passed). Se `test_depara_cobre_todos_os_itens_plus` falhar, o de-para está incompleto — adicionar o código faltante.

- [ ] **Step 4: Commit**

```bash
git add skills/orcamento-decor/references/depara-catalogo.json tests/test_fetch_catalogo.py
git commit -m "feat(orcamento): de-para item->produto da base Supabase"
```

---

### Task 2: Funções puras de extração e normalização

**Files:**
- Create: `skills/orcamento-decor/scripts/fetch_catalogo.py`
- Test: `tests/test_fetch_catalogo.py`

- [ ] **Step 1: Escrever os testes (falham)**

Append em `tests/test_fetch_catalogo.py`:

```python
def test_extrai_bundle_path_do_html():
    from fetch_catalogo import extrair_bundle_path
    html = '<html><script type="module" src="/assets/index-DcpALHpp.js"></script></html>'
    assert extrair_bundle_path(html) == "assets/index-DcpALHpp.js"


def test_extrai_bundle_path_retorna_none_sem_match():
    from fetch_catalogo import extrair_bundle_path
    assert extrair_bundle_path("<html></html>") is None


def test_extrai_anon_key_jwt():
    from fetch_catalogo import extrair_anon_key
    js = 'const k="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.abc-_DEF123";'
    assert extrair_anon_key(js) == "eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.abc-_DEF123"


def test_extrai_anon_key_retorna_none_sem_match():
    from fetch_catalogo import extrair_anon_key
    assert extrair_anon_key("sem token aqui") is None


def test_normalizar_corrige_double_utf8():
    from fetch_catalogo import normalizar
    assert normalizar("SofÃ¡-cama") == "Sofá-cama"


def test_normalizar_deixa_texto_limpo_intacto():
    from fetch_catalogo import normalizar
    assert normalizar("Cooktop 2 Bocas") == "Cooktop 2 Bocas"
```

- [ ] **Step 2: Rodar e verificar que falha**

Run: `python -m pytest tests/test_fetch_catalogo.py -k "bundle or anon or normalizar" -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'fetch_catalogo'`.

- [ ] **Step 3: Implementar as funções puras**

Create `skills/orcamento-decor/scripts/fetch_catalogo.py`:

```python
"""Lê o catálogo de preços ao vivo do Supabase (app seazone-decor-interno).

Substitui o download do CSV do Drive. Resolve a anon key a partir do bundle de
produção (RLS libera leitura anon), consulta a tabela `produto` pelos códigos do
de-para e devolve JSON no mesmo formato que ler_catalogo.py produzia:

  { "<codigo-item>": {"nome","categoria","valor_unitario","unidade"}, ... }

Uso:
  python fetch_catalogo.py > tmp/produtos.json
  python fetch_catalogo.py --depara skills/orcamento-decor/references/depara-catalogo.json
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

SITE_URL = "https://seazone-decor-interno.seazone.properties"
SUPABASE_URL = "https://cjbsotszriddpadznhvk.supabase.co"
DEPARA_PADRAO = Path(__file__).parent.parent / "references/depara-catalogo.json"

_RE_BUNDLE = re.compile(r"assets/[^\"']+\.js")
_RE_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")


def extrair_bundle_path(html: str) -> str | None:
    m = _RE_BUNDLE.search(html or "")
    return m.group(0) if m else None


def extrair_anon_key(js: str) -> str | None:
    m = _RE_JWT.search(js or "")
    return m.group(0) if m else None


def normalizar(s):
    """Corrige double-encoding (UTF-8 lido como latin1): 'Ã§' -> 'ç'."""
    if not isinstance(s, str):
        return s
    if any(c in s for c in ("Ã", "Â", "�")):
        try:
            return s.encode("latin1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return s
    return s
```

- [ ] **Step 4: Rodar e verificar que passa**

Run: `python -m pytest tests/test_fetch_catalogo.py -k "bundle or anon or normalizar" -v`
Expected: PASS (6 passed).

- [ ] **Step 5: Commit**

```bash
git add skills/orcamento-decor/scripts/fetch_catalogo.py tests/test_fetch_catalogo.py
git commit -m "feat(orcamento): extracao de anon key/bundle e normalizacao de encoding"
```

---

### Task 3: Parse da resposta da API → produtos.json

**Files:**
- Modify: `skills/orcamento-decor/scripts/fetch_catalogo.py`
- Create: `tests/fixtures/produto_api_sample.json`
- Test: `tests/test_fetch_catalogo.py`

- [ ] **Step 1: Criar a fixture de resposta da API**

Create `tests/fixtures/produto_api_sample.json`:

```json
[
  {"codigo": 73, "nome": "Gabinete inferior", "valor": 2700.0, "subcategoria_codigo": "2.1.1"},
  {"codigo": 190, "nome": "Cama box Queen c\\ cama auxiliar", "valor": 3221.22, "subcategoria_codigo": "2.1.6"},
  {"codigo": 333, "nome": "SofÃ¡-cama | Belize Aveia", "valor": 3049.0, "subcategoria_codigo": "2.1.6"},
  {"codigo": 449, "nome": "Cooktop | 2 Bocas", "valor": 1319.0, "subcategoria_codigo": "2.1.8"}
]
```

- [ ] **Step 2: Escrever os testes do parse (falham)**

Append em `tests/test_fetch_catalogo.py`:

```python
FIXTURES = Path(__file__).parent / "fixtures"


def test_parsear_resposta_mapeia_codigo_item_para_preco():
    from fetch_catalogo import parsear_resposta
    texto = (FIXTURES / "produto_api_sample.json").read_text(encoding="utf-8")
    depara = {"MRC0002": 73, "MOB0001": 190, "MOB0003": 333, "ELE0006": 449}
    produtos = parsear_resposta(texto, depara)
    assert produtos["MRC0002"]["valor_unitario"] == 2700.0
    assert produtos["ELE0006"]["valor_unitario"] == 1319.0


def test_parsear_resposta_normaliza_nome():
    from fetch_catalogo import parsear_resposta
    texto = (FIXTURES / "produto_api_sample.json").read_text(encoding="utf-8")
    depara = {"MOB0003": 333}
    produtos = parsear_resposta(texto, depara)
    assert produtos["MOB0003"]["nome"] == "Sofá-cama | Belize Aveia"


def test_parsear_resposta_ignora_codigo_fora_do_depara():
    from fetch_catalogo import parsear_resposta
    texto = '[{"codigo": 999, "nome": "X", "valor": 10.0, "subcategoria_codigo": "2.1.1"}]'
    produtos = parsear_resposta(texto, {"MRC0002": 73})
    assert produtos == {}


def test_carregar_depara_le_arquivo_padrao():
    from fetch_catalogo import carregar_depara
    depara = carregar_depara(None)
    assert depara["MRC0002"] == 73
```

- [ ] **Step 3: Rodar e verificar que falha**

Run: `python -m pytest tests/test_fetch_catalogo.py -k "parsear or carregar_depara" -v`
Expected: FAIL com `ImportError: cannot import name 'parsear_resposta'`.

- [ ] **Step 4: Implementar `parsear_resposta` e `carregar_depara`**

Append em `skills/orcamento-decor/scripts/fetch_catalogo.py`:

```python
def carregar_depara(caminho) -> dict:
    p = Path(caminho) if caminho else DEPARA_PADRAO
    return json.loads(p.read_text(encoding="utf-8"))


def parsear_resposta(json_text: str, depara: dict) -> dict:
    """Recebe linhas da API (list[dict]) + de-para (codigo-item -> produto.codigo)
    e devolve {codigo-item: {nome, categoria, valor_unitario, unidade}}."""
    linhas = json.loads(json_text)
    # reverso: produto.codigo -> [codigos-item]
    reverso: dict[int, list[str]] = {}
    for cod_item, cod_base in depara.items():
        reverso.setdefault(cod_base, []).append(cod_item)

    produtos: dict[str, dict] = {}
    for row in linhas:
        cod_base = row.get("codigo")
        for cod_item in reverso.get(cod_base, []):
            produtos[cod_item] = {
                "nome": normalizar(row.get("nome", "")),
                "categoria": row.get("subcategoria_codigo", "") or "",
                "valor_unitario": float(row.get("valor") or 0.0),
                "unidade": "un",
            }
    return produtos
```

- [ ] **Step 5: Rodar e verificar que passa**

Run: `python -m pytest tests/test_fetch_catalogo.py -k "parsear or carregar_depara" -v`
Expected: PASS (4 passed).

- [ ] **Step 6: Commit**

```bash
git add skills/orcamento-decor/scripts/fetch_catalogo.py tests/fixtures/produto_api_sample.json tests/test_fetch_catalogo.py
git commit -m "feat(orcamento): parse da resposta do catalogo Supabase para produtos.json"
```

---

### Task 4: Wrapper de rede + `main()` (com fetcher injetável)

**Files:**
- Modify: `skills/orcamento-decor/scripts/fetch_catalogo.py`
- Test: `tests/test_fetch_catalogo.py`

- [ ] **Step 1: Escrever o teste do fluxo com fetcher fake (falha)**

Append em `tests/test_fetch_catalogo.py`:

```python
def test_buscar_catalogo_orquestra_com_http_fake():
    from fetch_catalogo import buscar_catalogo

    def http_fake(url, headers=None):
        if url.endswith("seazone-decor-interno.seazone.properties/"):
            return '<script src="/assets/index-ABC123.js"></script>'
        if url.endswith("assets/index-ABC123.js"):
            return 'x="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiYW5vbiJ9.sig-_123";'
        if "/rest/v1/produto" in url:
            assert headers and headers.get("apikey", "").startswith("eyJ")
            return '[{"codigo": 73, "nome": "Gabinete inferior", "valor": 2700.0, "subcategoria_codigo": "2.1.1"}]'
        raise AssertionError(f"URL inesperada: {url}")

    produtos = buscar_catalogo({"MRC0002": 73}, http_get=http_fake)
    assert produtos["MRC0002"]["valor_unitario"] == 2700.0


def test_buscar_catalogo_sem_bundle_levanta_erro():
    from fetch_catalogo import buscar_catalogo, CatalogoError

    def http_fake(url, headers=None):
        return "<html>sem bundle</html>"

    import pytest
    with pytest.raises(CatalogoError):
        buscar_catalogo({"MRC0002": 73}, http_get=http_fake)
```

- [ ] **Step 2: Rodar e verificar que falha**

Run: `python -m pytest tests/test_fetch_catalogo.py -k "buscar_catalogo" -v`
Expected: FAIL com `ImportError: cannot import name 'buscar_catalogo'`.

- [ ] **Step 3: Implementar wrapper, `buscar_catalogo` e `main`**

Append em `skills/orcamento-decor/scripts/fetch_catalogo.py`:

```python
class CatalogoError(RuntimeError):
    pass


def _http_get(url: str, headers: dict | None = None) -> str:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def buscar_catalogo(depara: dict, http_get=_http_get) -> dict:
    html = http_get(SITE_URL + "/")
    bundle = extrair_bundle_path(html)
    if not bundle:
        raise CatalogoError("Bundle JS não encontrado no HTML de produção.")
    js = http_get(f"{SITE_URL}/{bundle}")
    key = extrair_anon_key(js)
    if not key:
        raise CatalogoError("Anon key não encontrada no bundle.")
    codigos = ",".join(str(c) for c in sorted(set(depara.values())))
    url = (f"{SUPABASE_URL}/rest/v1/produto"
           f"?select=codigo,nome,valor,subcategoria_codigo&codigo=in.({codigos})")
    corpo = http_get(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    return parsear_resposta(corpo, depara)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Lê o catálogo de preços do Supabase")
    p.add_argument("--depara", help="Caminho do de-para (default: references/depara-catalogo.json)")
    args = p.parse_args()
    try:
        depara = carregar_depara(args.depara)
        produtos = buscar_catalogo(depara)
        print(json.dumps(produtos, ensure_ascii=False, indent=2))
    except (CatalogoError, OSError, ValueError) as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar e verificar que passa**

Run: `python -m pytest tests/test_fetch_catalogo.py -v`
Expected: PASS (todos os testes do arquivo).

- [ ] **Step 5: Rodar a suíte inteira (sem regressão)**

Run: `python -m pytest -q`
Expected: a suíte existente (83 testes) + os novos, todos passando.

- [ ] **Step 6: Commit**

```bash
git add skills/orcamento-decor/scripts/fetch_catalogo.py tests/test_fetch_catalogo.py
git commit -m "feat(orcamento): leitura ao vivo do catalogo via PostgREST + anon key"
```

---

### Task 5: Smoke test ao vivo + atualizar SKILL.md e schema

**Files:**
- Modify: `skills/orcamento-decor/SKILL.md`
- Modify: `skills/orcamento-decor/references/catalogo-schema.md`

- [ ] **Step 1: Smoke test contra a base real**

Run: `python skills/orcamento-decor/scripts/fetch_catalogo.py > tmp/produtos.json`
Expected: JSON com ~33 entradas; conferir 3 valores-âncora:
- `MRC0002` (gabinete inferior) ≈ 2700
- `ELE0006` (cooktop) ≈ 1319
- `MOB0001` (cama queen) ≈ 3221

Se a rede falhar, o script sai com `{"erro": ...}` em stderr e código 1 — esperado; nesse caso `montar_orcamento.py` roda sem `--produtos` (usa os valores default).

- [ ] **Step 2: Atualizar os passos 2–3 da SKILL.md**

Em `skills/orcamento-decor/SKILL.md`, substituir o bloco dos passos "### 2. Baixar catalogo do Drive" e "### 3. Parsear catalogo" por:

```markdown
### 2. Ler o catálogo de preços (Supabase, ao vivo)

A base de valores agora é o app **seazone-decor-interno** (Supabase). Leia ao vivo:

```bash
python skills/orcamento-decor/scripts/fetch_catalogo.py > tmp/produtos.json
```

O script resolve a anon key do bundle de produção, consulta os 33 produtos do
de-para (`references/depara-catalogo.json`) e devolve `produtos.json` no formato
que `montar_orcamento.py` consome. Se a rede/base falhar (sai com `{"erro": ...}`
em stderr, código 1): pule e gere com os valores default (omita `--produtos` no passo 5).
```

- [ ] **Step 3: Atualizar o catalogo-schema.md**

Substituir o conteúdo de `skills/orcamento-decor/references/catalogo-schema.md` por:

```markdown
# Fonte do catálogo de preços

A base de valores migrou do Sheet do Drive (`db002_produtos`) para o app interno
**seazone-decor-interno** (Supabase `cjbsotszriddpadznhvk`, tabela `produto`).

## Como a skill lê
`scripts/fetch_catalogo.py`:
1. GET `https://seazone-decor-interno.seazone.properties/` → acha `assets/index-*.js`.
2. GET do bundle → extrai a anon key (JWT) embutida.
3. GET `…/rest/v1/produto?select=codigo,nome,valor,subcategoria_codigo&codigo=in.(...)`
   com header `apikey` (RLS libera leitura anon).
4. Mapeia `produto.codigo` → código-item via `depara-catalogo.json` e devolve
   `{codigo-item: {nome, categoria, valor_unitario, unidade}}`.

## De-para (`depara-catalogo.json`)
Liga cada um dos 33 itens-template da skill a UM `produto.codigo` exato da base,
escolhido pelo produto mais usado nos memoriais Plus reais (`produto_tipologia`).
Regra de valor: SEMPRE seguir o que a base usa (fonte mais atualizada); sem override manual.

## Encoding
Campos texto vêm com double-encoding (UTF-8 lido como latin1). `normalizar()` corrige.

## Fallback
`ler_catalogo.py` (parse de CSV) permanece como fallback offline.
```

- [ ] **Step 4: Rodar a suíte mais uma vez**

Run: `python -m pytest -q`
Expected: tudo verde.

- [ ] **Step 5: Commit**

```bash
git add skills/orcamento-decor/SKILL.md skills/orcamento-decor/references/catalogo-schema.md
git commit -m "docs(orcamento): SKILL e schema apontam para o catalogo Supabase"
```

---

## Self-Review

**Spec coverage (Fase A do design):**
- "Novo leitor lê `valor` da base Supabase" → Tasks 2–4 (`fetch_catalogo.py`). ✓
- "Anon key do bundle em runtime" → Task 2 (`extrair_anon_key`/`extrair_bundle_path`) + Task 4 (`buscar_catalogo`). ✓
- "De-para item→produto exato, versionado" → Task 1. ✓
- "Normalizar double-UTF8" → Task 2 (`normalizar`). ✓
- "`montar_orcamento.py` consome igual" → garantido pelo formato de saída idêntico (Task 3) + suíte sem regressão (Task 4 Step 5). ✓
- "Regra de valor: sempre a base, sem override" → documentado no schema (Task 5). ✓
- Fallback offline preservado → `ler_catalogo.py` intacto; nota no schema (Task 5). ✓

**Placeholder scan:** sem TBD/TODO; todo passo de código tem código completo. ✓

**Type consistency:** `extrair_bundle_path`, `extrair_anon_key`, `normalizar`, `carregar_depara`, `parsear_resposta`, `buscar_catalogo(depara, http_get=...)`, `CatalogoError`, `_http_get(url, headers)` — nomes idênticos entre tasks e testes. Saída de `parsear_resposta`/`buscar_catalogo` = `{codigo-item: {nome, categoria, valor_unitario, unidade}}`, que `montar_orcamento.py` lê via `v["nome"]`, `v["categoria"]`, `v["valor_unitario"]`, `v.get("unidade","un")`. ✓

## Fora de escopo (próximas fases)
Fase B (BOM do Revit, ramificação área comum no Rosa Sul), C (matching), D (renders), E (saída) — planos próprios depois que a Fase A fechar.
