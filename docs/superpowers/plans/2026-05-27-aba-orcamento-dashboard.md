# Aba Orçamento no Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Habilitar a aba "Orçamento" do dashboard, mostrando custo de decor por tipologia por empreendimento (resumo embutido + links pro Drive), alimentada por um `orcamentos.js` que a skill `orcamento-decor` passa a escrever.

**Architecture:** Novo arquivo de dados `dashboard/data/orcamentos.js` (`window.ORCAMENTOS`), paralelo a `tipologias.js`. Um script Python testável (`gerar_dashboard_js.py`) faz upsert de um Spot nesse arquivo. O dashboard ganha um painel `#panel-orcamento` (HTML), uma IIFE de render em `app.js` e ajustes mínimos de CSS. A skill `orcamento-decor` passa a chamar o script no lugar de mexer em `tipologias.js`.

**Tech Stack:** HTML/CSS/JS estático (sem framework), Python 3.12 stdlib (`json`, `argparse`), pytest. Verificação de UI manual no browser (`python -m http.server`).

---

## File Structure

```
skills/orcamento-decor/scripts/
  gerar_dashboard_js.py          # NOVO: upsert de Spot em orcamentos.js (testável)
skills/orcamento-decor/SKILL.md  # MODIFICA passo 8: chama gerar_dashboard_js.py

tests/
  test_gerar_dashboard_js.py     # NOVO

dashboard/
  data/orcamentos.js             # NOVO: window.ORCAMENTOS (seed Natal Spot p/ vitrine)
  index.html                     # MODIFICA: habilita aba + #panel-orcamento + <script>
  app.js                         # MODIFICA: registra painel + nova IIFE de render
  styles.css                     # MODIFICA: chip de estilo + coluna de link
```

Cópia instalada da skill em `C:\Users\Seazone\Claude\.claude\skills\orcamento-decor\` é re-sincronizada no fim.

---

## Task 1: gerar_dashboard_js.py + testes

**Files:**
- Create: `skills/orcamento-decor/scripts/gerar_dashboard_js.py`
- Create: `tests/test_gerar_dashboard_js.py`

- [ ] **Step 1: Escrever os testes**

Criar `tests/test_gerar_dashboard_js.py`:

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from gerar_dashboard_js import (
    parsear_js, serializar_js, construir_entrada, upsert_spot,
)

MEMORIAIS = {
    "memoriais": [
        {"tipologia": "A", "descricao": "Sem · Padrão · Cap. 2", "total_geral": 41766.0},
        {"tipologia": "B", "descricao": "Garden · Padrão · Cap. 4", "total_geral": 53079.0},
    ]
}
MEMORIAL_URLS = {"A": "https://drive/A", "B": "https://drive/B"}


def test_parsear_js_vazio_quando_string_vazia():
    assert parsear_js("") == {"index": [], "spots": {}}


def test_parsear_js_le_window_orcamentos():
    texto = 'window.ORCAMENTOS = {"index": [], "spots": {"x": 1}};\n'
    assert parsear_js(texto) == {"index": [], "spots": {"x": 1}}


def test_serializar_js_roundtrip():
    dados = {"index": [{"slug": "natal-spot"}], "spots": {"natal-spot": {"spot": "Natal"}}}
    texto = serializar_js(dados)
    assert texto.startswith("//")
    assert "window.ORCAMENTOS =" in texto
    assert parsear_js(texto) == dados


def test_construir_entrada_index_tem_campos():
    idx, _ = construir_entrada(
        spot="Natal Spot", codigo="6953", slug="natal-spot", estilo="Clean",
        consolidado_url="https://drive/cons", memoriais=MEMORIAIS,
        memorial_urls=MEMORIAL_URLS, gerado_em="2026-05-27")
    assert idx["spot"] == "Natal Spot"
    assert idx["slug"] == "natal-spot"
    assert idx["estilo"] == "Clean"
    assert idx["pacote"] == "Plus"
    assert idx["total_tipologias"] == 2
    assert idx["consolidado_url"] == "https://drive/cons"


def test_construir_entrada_spot_tem_tipologias_com_custo_e_url():
    _, sp = construir_entrada(
        spot="Natal Spot", codigo="6953", slug="natal-spot", estilo="Clean",
        consolidado_url="https://drive/cons", memoriais=MEMORIAIS,
        memorial_urls=MEMORIAL_URLS, gerado_em="2026-05-27")
    a = next(t for t in sp["tipologias"] if t["tipologia"] == "A")
    assert a["descricao"] == "Sem · Padrão · Cap. 2"
    assert a["custo"] == 41766.0
    assert a["memorial_url"] == "https://drive/A"


def test_construir_entrada_url_ausente_vira_hash():
    _, sp = construir_entrada(
        spot="X", codigo="1", slug="x", estilo="Clean",
        consolidado_url="https://drive/cons", memoriais=MEMORIAIS,
        memorial_urls={"A": "https://drive/A"}, gerado_em="2026-05-27")
    b = next(t for t in sp["tipologias"] if t["tipologia"] == "B")
    assert b["memorial_url"] == "#"


def test_upsert_adiciona_novo_spot():
    base = {"index": [], "spots": {}}
    idx = {"slug": "natal-spot", "spot": "Natal Spot"}
    sp = {"spot": "Natal Spot", "tipologias": []}
    res = upsert_spot(base, "natal-spot", idx, sp)
    assert len(res["index"]) == 1
    assert res["spots"]["natal-spot"] == sp


def test_upsert_substitui_spot_existente_sem_duplicar():
    base = {
        "index": [{"slug": "natal-spot", "spot": "Velho"}],
        "spots": {"natal-spot": {"spot": "Velho"}},
    }
    idx = {"slug": "natal-spot", "spot": "Novo"}
    sp = {"spot": "Novo", "tipologias": []}
    res = upsert_spot(base, "natal-spot", idx, sp)
    assert len(res["index"]) == 1
    assert res["index"][0]["spot"] == "Novo"
    assert res["spots"]["natal-spot"]["spot"] == "Novo"
```

- [ ] **Step 2: Rodar pra confirmar falha**

Run: `python -m pytest tests/test_gerar_dashboard_js.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'gerar_dashboard_js'`

- [ ] **Step 3: Escrever a implementação**

Criar `skills/orcamento-decor/scripts/gerar_dashboard_js.py`:

```python
"""Faz upsert de um Spot no dashboard/data/orcamentos.js (window.ORCAMENTOS).

Lê o orcamentos.js existente (se houver), substitui/adiciona o Spot pelo slug
e reescreve o arquivo. NUNCA toca tipologias.js.

Uso:
  python gerar_dashboard_js.py \
    --orcamentos-js dashboard/data/orcamentos.js \
    --spot "Natal Spot" --codigo 6953 --slug natal-spot \
    --estilo Clean --consolidado-url "https://docs.google.com/.../edit" \
    --memoriais tmp/memoriais.json \
    --memorial-urls tmp/memorial_urls.json \
    --gerado-em 2026-05-27
"""
import argparse
import json
import sys
from pathlib import Path

_PREFIXO = "window.ORCAMENTOS ="
_CABECALHO = "// dashboard/data/orcamentos.js -- reescrito pela skill orcamento-decor.\n"


def parsear_js(texto: str) -> dict:
    t = (texto or "").strip()
    if not t:
        return {"index": [], "spots": {}}
    # remove linhas de comentario //
    linhas = [ln for ln in t.splitlines() if not ln.strip().startswith("//")]
    t = "\n".join(linhas).strip()
    if t.startswith(_PREFIXO):
        t = t[len(_PREFIXO):].strip()
    if t.endswith(";"):
        t = t[:-1].strip()
    if not t:
        return {"index": [], "spots": {}}
    return json.loads(t)


def serializar_js(orcamentos: dict) -> str:
    corpo = json.dumps(orcamentos, ensure_ascii=False, indent=2)
    return f"{_CABECALHO}{_PREFIXO} {corpo};\n"


def construir_entrada(
    spot: str, codigo: str, slug: str, estilo: str,
    consolidado_url: str, memoriais: dict,
    memorial_urls: dict, gerado_em: str,
) -> tuple[dict, dict]:
    lista = memoriais.get("memoriais", [])
    tipologias = [
        {
            "tipologia": m["tipologia"],
            "descricao": m["descricao"],
            "custo": m["total_geral"],
            "memorial_url": memorial_urls.get(m["tipologia"], "#"),
        }
        for m in lista
    ]
    index_entry = {
        "spot": spot, "codigo": str(codigo), "slug": slug,
        "estilo": estilo, "pacote": "Plus", "gerado_em": gerado_em,
        "total_tipologias": len(tipologias),
        "consolidado_url": consolidado_url,
    }
    spot_entry = {
        "spot": spot, "estilo": estilo, "pacote": "Plus",
        "consolidado_url": consolidado_url,
        "tipologias": tipologias,
    }
    return index_entry, spot_entry


def upsert_spot(orcamentos: dict, slug: str, index_entry: dict, spot_entry: dict) -> dict:
    index = [e for e in orcamentos.get("index", []) if e.get("slug") != slug]
    index.append(index_entry)
    spots = dict(orcamentos.get("spots", {}))
    spots[slug] = spot_entry
    return {"index": index, "spots": spots}


def main() -> None:
    p = argparse.ArgumentParser(description="Upsert de Spot em orcamentos.js")
    p.add_argument("--orcamentos-js", type=Path, required=True)
    p.add_argument("--spot", required=True)
    p.add_argument("--codigo", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--estilo", required=True)
    p.add_argument("--consolidado-url", required=True)
    p.add_argument("--memoriais", type=Path, required=True)
    p.add_argument("--memorial-urls", type=Path, required=True)
    p.add_argument("--gerado-em", required=True)
    args = p.parse_args()

    memoriais = json.loads(args.memoriais.read_text(encoding="utf-8"))
    memorial_urls = json.loads(args.memorial_urls.read_text(encoding="utf-8"))

    atual = parsear_js(args.orcamentos_js.read_text(encoding="utf-8")) \
        if args.orcamentos_js.exists() else {"index": [], "spots": {}}

    idx, sp = construir_entrada(
        spot=args.spot, codigo=args.codigo, slug=args.slug, estilo=args.estilo,
        consolidado_url=args.consolidado_url, memoriais=memoriais,
        memorial_urls=memorial_urls, gerado_em=args.gerado_em)

    novo = upsert_spot(atual, args.slug, idx, sp)
    args.orcamentos_js.write_text(serializar_js(novo), encoding="utf-8")
    print(f"orcamentos.js atualizado: {args.slug} ({len(sp['tipologias'])} tipologias)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar pra confirmar que passa**

Run: `python -m pytest tests/test_gerar_dashboard_js.py -v`
Expected: 8 passed

- [ ] **Step 5: Rodar a suite completa (nada quebrou)**

Run: `python -m pytest tests/ -q`
Expected: 71 passed (63 anteriores + 8 novos)

- [ ] **Step 6: Commit**

```bash
git add skills/orcamento-decor/scripts/gerar_dashboard_js.py tests/test_gerar_dashboard_js.py
git commit -m "feat(orcamento): gerar_dashboard_js.py - upsert de Spot em orcamentos.js"
```

---

## Task 2: Seed do orcamentos.js (Natal Spot, pra vitrine)

**Files:**
- Create: `dashboard/data/orcamentos.js`

Gera um `orcamentos.js` real com o Natal Spot, usando os scripts já existentes, pra os avaliadores verem a aba funcionando. Os links de Drive são placeholders (a skill grava os reais quando rodar contra o Drive).

- [ ] **Step 1: Calcular os custos do Natal Spot**

No PowerShell, criar o input com as 5 tipologias reais do Natal (de `dashboard/data/tipologias.js`):

```powershell
New-Item -ItemType Directory -Force "tmp"
$tips = '[{"tipologia":"A","terraco":"Sem","tipo":"Padrão","capacidade":2},{"tipologia":"B","terraco":"Sem","tipo":"Padrão","capacidade":3},{"tipologia":"C","terraco":"Sem","tipo":"Padrão","capacidade":5},{"tipologia":"D","terraco":"Sacada","tipo":"Padrão","capacidade":3},{"tipologia":"E","terraco":"Sacada","tipo":"Padrão","capacidade":5}]'
$tips | Out-File -Encoding utf8 "tmp\natal_tips.json"
python skills/orcamento-decor/scripts/montar_orcamento.py --tipologias tmp\natal_tips.json --estilo clean --spot "Natal Spot" | Out-File -Encoding utf8 "tmp\memoriais.json"
```

- [ ] **Step 2: Criar os memorial_urls placeholder**

A URL real só existe após rodar a skill no Drive. Usar a URL do Sheet de tipologias do Natal (existe e abre algo coerente) como placeholder do consolidado, e `#` nos memoriais:

```powershell
'{"A":"#","B":"#","C":"#","D":"#","E":"#"}' | Out-File -Encoding utf8 "tmp\memorial_urls.json"
```

- [ ] **Step 3: Gerar o orcamentos.js**

```powershell
python skills/orcamento-decor/scripts/gerar_dashboard_js.py `
  --orcamentos-js dashboard/data/orcamentos.js `
  --spot "Natal Spot" --codigo 6953 --slug natal-spot `
  --estilo Clean `
  --consolidado-url "https://docs.google.com/spreadsheets/d/1Ffn359MFIgtERfKWiR-UfMFJVUOWDotSaSQLm8PxXQ8/edit" `
  --memoriais tmp\memoriais.json `
  --memorial-urls tmp\memorial_urls.json `
  --gerado-em 2026-05-27
```

- [ ] **Step 4: Conferir o arquivo gerado**

Run: `python -c "import json; t=open('dashboard/data/orcamentos.js',encoding='utf-8').read(); s=t.split('=',1)[1].rsplit(';',1)[0]; d=json.loads(s); print(len(d['index']), 'spot(s)'); print([ (x['tipologia'], x['custo']) for x in d['spots']['natal-spot']['tipologias'] ])"`
Expected: imprime `1 spot(s)` e a lista de 5 tipologias com custos > 0 (ex: A ~41766, C maior que A).

- [ ] **Step 5: Commit**

```bash
git add dashboard/data/orcamentos.js
git commit -m "feat(dashboard): seed orcamentos.js com Natal Spot (vitrine)"
```

---

## Task 3: HTML — habilitar aba + painel + script

**Files:**
- Modify: `dashboard/index.html`

- [ ] **Step 1: Habilitar a aba na navegação**

Em `dashboard/index.html`, trocar a linha 23:

```html
    <button class="tab is-soon" disabled>Orçamento <em>em breve</em></button>
```

por:

```html
    <button class="tab" data-tab="orcamento" role="tab">Orçamento</button>
```

- [ ] **Step 2: Adicionar o painel `#panel-orcamento`**

Em `dashboard/index.html`, logo ANTES da linha `<script src="data/padrao-spot.js"></script>` (atual linha 129), inserir o novo `<main>`:

```html
  <main id="panel-orcamento" class="panel" hidden>
    <section class="hero reveal">
      <p class="eyebrow">Orçamento de decor · Lançamentos</p>
      <h1>Custo de decor por <span class="hl">empreendimento</span>.</h1>
      <p class="lede">O orçamento preliminar de decor (pacote Plus) por tipologia, gerado a partir do catálogo. Busque o empreendimento, veja o custo por tipologia e abra os memoriais no Drive.</p>
    </section>

    <section class="block reveal">
      <div class="block-head"><span class="num">+</span><h2>Gerar um orçamento</h2></div>
      <p class="howto-lede">Peça ao Claude e ele monta o memorial descritivo de decor de cada tipologia — puxando preços do catálogo e criando os Sheets no Drive. É a skill <code>orcamento-decor</code>.</p>
      <ol class="howto-steps">
        <li><strong>Peça ao Claude</strong> com o comando abaixo (ou <code>/orcamento-decor</code>).</li>
        <li>Ele <strong>identifica o estilo</strong> do Spot (Clean · Biofílico · Industrial · Bruma) — pergunta se ainda não estiver definido.</li>
        <li>Baixa o <strong>catálogo de produtos</strong> e lê as <strong>tipologias</strong> já geradas.</li>
        <li>Monta o <strong>memorial por tipologia</strong> (itens · qtd · preço · subtotais · taxas) no pacote <strong>Plus</strong>.</li>
        <li>Cria os <strong>Sheets no Drive</strong> (um por tipologia + um consolidado) e atualiza esta vitrine.</li>
      </ol>
      <div class="cmd-row">
        <code id="orc-howto-cmd">gera o orçamento do &lt;empreendimento&gt;</code>
        <button class="btn btn-primary" id="orc-howto-copy">Copiar comando</button>
      </div>
      <p class="howto-nota">Custos são <strong>referência (Plus 2026)</strong> — o memorial completo, com itens e preços, fica nos Sheets do Drive.</p>
    </section>

    <section class="block reveal">
      <div class="search-bar">
        <input id="orc-search" type="text" placeholder="Buscar empreendimento (nome ou código)…" autocomplete="off" />
      </div>
      <div id="orc-list" class="spot-list"></div>
      <div id="orc-empty" class="spot-empty" hidden></div>
    </section>

    <footer class="foot">
      <span>Seazone Investimentos · Padrão Spot</span>
      <span>Seu lugar fora de casa</span>
    </footer>
  </main>

```

- [ ] **Step 3: Adicionar o `<script>` do orcamentos.js**

Em `dashboard/index.html`, logo APÓS `<script src="data/tipologias.js"></script>` (atual linha 130), inserir:

```html
  <script src="data/orcamentos.js"></script>
```

- [ ] **Step 4: Commit**

```bash
git add dashboard/index.html
git commit -m "feat(dashboard): habilita aba Orcamento + painel + script"
```

---

## Task 4: JS — registrar painel + IIFE de render

**Files:**
- Modify: `dashboard/app.js`

- [ ] **Step 1: Registrar o painel orcamento na navegação por abas**

Em `dashboard/app.js`, na IIFE de navegação (atual linha 110), trocar:

```javascript
  const panels = { logica: document.getElementById("panel-logica"), tipologias: document.getElementById("panel-tipologias") };
```

por:

```javascript
  const panels = {
    logica: document.getElementById("panel-logica"),
    tipologias: document.getElementById("panel-tipologias"),
    orcamento: document.getElementById("panel-orcamento"),
  };
```

- [ ] **Step 2: Adicionar a IIFE de render do orçamento**

Em `dashboard/app.js`, no FINAL do arquivo (após a IIFE de Tipologias, atual linha 220), adicionar:

```javascript

// ---------- Aba: Orçamento por Spot (vitrine) ----------
(function () {
  const O = window.ORCAMENTOS;
  if (!O) return;
  const $ = (s) => document.querySelector(s);
  const el = (tag, cls, html) => { const n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; };

  const list = $("#orc-list");
  const empty = $("#orc-empty");
  const input = $("#orc-search");

  const brl = (v) => "R$ " + Number(v).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  function tabelaHTML(spot) {
    const rows = spot.tipologias.map((t) => {
      const link = t.memorial_url && t.memorial_url !== "#"
        ? `<a class="memorial-link" href="${t.memorial_url}" target="_blank" rel="noopener">Memorial ↗</a>`
        : `<span class="memorial-link off">—</span>`;
      return `
      <tr>
        <td class="t-tip">${t.tipologia}</td>
        <td class="t-desc">${t.descricao}</td>
        <td class="t-custo">${brl(t.custo)}</td>
        <td>${link}</td>
      </tr>`;
    }).join("");
    return `<div class="table-wrap"><table class="matriz tabela-orc">
      <thead><tr><th>Tipologia</th><th>Descrição</th><th>Custo estimado</th><th>Memorial</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  }

  function card(item) {
    const c = el("div", "spot-card");
    const chip = `<div class="fontes"><span class="estilo-chip">${item.estilo} · ${item.pacote}</span></div>`;
    const cons = item.consolidado_url && item.consolidado_url !== "#"
      ? `<a class="btn btn-ghost" href="${item.consolidado_url}" target="_blank" rel="noopener">Abrir consolidado no Drive ↗</a>`
      : "";
    c.innerHTML = `
      <div class="spot-card-top">
        <div>
          <h3>${item.spot} <span class="spot-cod">${item.codigo}</span></h3>
          <p class="spot-meta">${item.total_tipologias} tipologias · gerado em ${item.gerado_em}</p>
        </div>
        ${chip}
      </div>
      <div class="spot-actions">
        <button class="btn btn-primary" data-ver="${item.slug}">Ver custos</button>
        ${cons}
      </div>
      <div class="spot-tabela" hidden></div>`;
    c.querySelector("[data-ver]").addEventListener("click", (e) => {
      const box = c.querySelector(".spot-tabela");
      const btn = e.currentTarget;
      if (box.hidden) {
        if (!box.dataset.loaded) { box.innerHTML = tabelaHTML(O.spots[item.slug]); box.dataset.loaded = "1"; }
        box.hidden = false; btn.textContent = "Ocultar custos";
      } else { box.hidden = true; btn.textContent = "Ver custos"; }
    });
    return c;
  }

  function semMatch(termo) {
    empty.hidden = false;
    list.innerHTML = "";
    const cmd = `gera o orçamento do ${termo || "<empreendimento>"}`;
    empty.innerHTML = `
      <p class="empty-title">Nenhum orçamento gerado para "<strong>${termo}</strong>".</p>
      <p class="empty-sub">Os orçamentos são gerados pelo Claude a partir do catálogo. Copie o comando e cole no Claude:</p>
      <div class="cmd-row"><code>${cmd}</code><button class="btn btn-primary" id="orc-copy-cmd">Pedir geração ao Claude</button></div>`;
    empty.querySelector("#orc-copy-cmd").addEventListener("click", () => {
      navigator.clipboard && navigator.clipboard.writeText(cmd);
      empty.querySelector("#orc-copy-cmd").textContent = "Comando copiado ✓";
    });
  }

  function render(termo) {
    const q = (termo || "").trim().toLowerCase();
    const itens = (O.index || []).filter((i) =>
      !q || i.spot.toLowerCase().includes(q) || String(i.codigo).toLowerCase().includes(q));
    if (!(O.index || []).length) { semMatch(termo); empty.querySelector(".empty-title").innerHTML = "Nenhum orçamento gerado ainda."; return; }
    if (!itens.length) { semMatch(termo); return; }
    empty.hidden = true;
    list.innerHTML = "";
    itens.forEach((i) => list.appendChild(card(i)));
  }

  input.addEventListener("input", (e) => render(e.target.value));
  render("");

  const howtoCopy = $("#orc-howto-copy");
  if (howtoCopy) {
    howtoCopy.addEventListener("click", () => {
      const txt = ($("#orc-howto-cmd") || {}).textContent || "";
      navigator.clipboard && navigator.clipboard.writeText(txt);
      howtoCopy.textContent = "Comando copiado ✓";
      setTimeout(() => { howtoCopy.textContent = "Copiar comando"; }, 2000);
    });
  }
})();
```

- [ ] **Step 3: Commit**

```bash
git add dashboard/app.js
git commit -m "feat(dashboard): render da aba Orcamento (IIFE) + nav"
```

---

## Task 5: CSS — chip de estilo + coluna de link

**Files:**
- Modify: `dashboard/styles.css`

- [ ] **Step 1: Adicionar estilos no fim do arquivo**

Em `dashboard/styles.css`, no FINAL do arquivo (após a linha 252), adicionar:

```css

/* ---------- Aba Orçamento ---------- */
.estilo-chip {
  flex: none; align-self: flex-start; font-size: 11px; font-weight: 700;
  letter-spacing: .03em; padding: 5px 12px; border-radius: 999px; white-space: nowrap;
  background: rgba(0,84,252,.12); color: var(--blue);
}
.tabela-orc td.t-tip { font-weight: 700; color: var(--blue); }
.tabela-orc td.t-desc { text-align: left; color: var(--ink-60); font-size: 13.5px; }
.tabela-orc td.t-custo { font-weight: 700; color: var(--navy); white-space: nowrap; }
.tabela-orc td { text-align: center; }
.memorial-link { font-size: 13px; font-weight: 700; color: var(--blue); text-decoration: none; }
.memorial-link:hover { text-decoration: underline; }
.memorial-link.off { color: #B7C0D8; font-weight: 400; }
```

- [ ] **Step 2: Commit**

```bash
git add dashboard/styles.css
git commit -m "style(dashboard): chip de estilo + tabela de custo da aba Orcamento"
```

---

## Task 6: Verificação no browser

**Files:** nenhum (verificação manual)

Use os preview tools (preferencial) ou `python -m http.server` na pasta `dashboard/`.

- [ ] **Step 1: Subir o servidor**

```bash
cd dashboard && python -m http.server 8000
```
(ou use `preview_start` apontando pra `dashboard/index.html`.)

- [ ] **Step 2: Conferir a navegação**

Abrir `http://localhost:8000/`. Clicar na aba "Orçamento". Confirmar:
- A aba aparece ativa (não mais "em breve").
- Hero + bloco "Gerar um orçamento" + busca + card do Natal Spot renderizam.

- [ ] **Step 3: Conferir o card e a tabela**

- O card mostra "Natal Spot 6953", chip "Clean · Plus", "5 tipologias".
- Clicar "Ver custos": tabela expande com 5 linhas (A–E), descrições, custos em `R$ XX.XXX,XX`.
- Custo de C (Cap.5) > custo de A (Cap.2).
- Coluna Memorial mostra "—" (placeholders `#` no seed).
- Clicar de novo: tabela colapsa, botão volta a "Ver custos".

- [ ] **Step 4: Conferir busca e empty state**

- Digitar "natal" → card aparece. Digitar "xyz" → empty state com comando `gera o orçamento do xyz` + botão copiar.

- [ ] **Step 5: Conferir que as outras abas seguem intactas**

- Aba "Tipologias por Spot": cards e tabelas renderizam normal (nada quebrou).
- Aba "Lógica & Regras": idem.

- [ ] **Step 6: Conferir console e responsivo**

- `preview_console_logs` (ou DevTools): sem erros JS.
- `preview_resize` mobile (ou janela estreita): card e tabela legíveis (scroll horizontal na tabela via `.table-wrap`).

- [ ] **Step 7: Screenshot de prova**

Capturar a aba Orçamento com a tabela expandida (`preview_screenshot`).

---

## Task 7: Atualizar SKILL.md (skill passa a escrever orcamentos.js)

**Files:**
- Modify: `skills/orcamento-decor/SKILL.md`

- [ ] **Step 1: Reescrever o passo 8**

Em `skills/orcamento-decor/SKILL.md`, substituir TODO o conteúdo do passo `### 8. Atualizar tipologias.js` (incluindo o título) por:

````markdown
### 8. Atualizar a vitrine do dashboard (orcamentos.js)

Durante os passos 6 e 7 você coletou: o `consolidado_url` (Sheet "Tipologias + Custo") e um `memorial_url` por tipologia (cada Sheet criado no passo 6). Monte um JSON de URLs e rode o script — ele faz upsert do Spot em `dashboard/data/orcamentos.js` sem tocar `tipologias.js`.

```bash
# tmp/memorial_urls.json  ->  {"A": "https://.../edit", "B": "https://.../edit", ...}
python skills/orcamento-decor/scripts/gerar_dashboard_js.py \
  --orcamentos-js dashboard/data/orcamentos.js \
  --spot "SPOT_NAME" --codigo CODIGO --slug SLUG \
  --estilo ESTILO_CAPITALIZADO \
  --consolidado-url "URL_DO_CONSOLIDADO" \
  --memoriais tmp/memoriais.json \
  --memorial-urls tmp/memorial_urls.json \
  --gerado-em AAAA-MM-DD
```

Faça commit:
```bash
git add dashboard/data/orcamentos.js
git commit -m "feat(orcamento): vitrine do SPOT_NAME no dashboard"
```

**NUNCA edite `tipologias.js` (arquivo da skill tabela-tipologias).**
````

- [ ] **Step 2: Commit**

```bash
git add skills/orcamento-decor/SKILL.md
git commit -m "docs(orcamento): passo 8 escreve orcamentos.js via gerar_dashboard_js.py"
```

---

## Task 8: Re-sincronizar skill instalada + push

**Files:**
- Copia `skills/orcamento-decor/` → `C:\Users\Seazone\Claude\.claude\skills\orcamento-decor\`

- [ ] **Step 1: Suite completa**

Run: `python -m pytest tests/ -q`
Expected: 71 passed.

- [ ] **Step 2: Re-instalar a skill globalmente (ganhou gerar_dashboard_js.py + SKILL.md novo)**

```powershell
$src = "C:\Users\Seazone\Claude\seazone\hackathon-investimentos\skills\orcamento-decor"
$dst = "C:\Users\Seazone\Claude\.claude\skills\orcamento-decor"
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
Copy-Item $src $dst -Recurse
Get-ChildItem $dst -Recurse -File | Select-Object FullName
```

- [ ] **Step 3: Push**

```bash
git push origin master
```

---

## Validação pós-implementação

1. A aba Orçamento abre e mostra o Natal Spot com custos por tipologia coerentes (Cap.5 > Cap.2).
2. Abas Tipologias e Lógica intactas.
3. Sem erros no console.
4. Ao rodar a skill `orcamento-decor` de verdade num Spot, o `orcamentos.js` é atualizado com URLs reais do Drive e o card passa a mostrar links "Memorial ↗" clicáveis.
