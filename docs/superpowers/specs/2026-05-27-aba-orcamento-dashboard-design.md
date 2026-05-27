# Design — Aba Orçamento no Dashboard

**Data:** 2026-05-27
**Projeto:** hackathon-investimentos (trilha Decor)
**Relacionado:** Fase 2 (skill `orcamento-decor`, já entregue)

---

## Contexto

A skill `orcamento-decor` (Fase 2) gera o memorial descritivo de decor por tipologia (pacote Plus) e grava Sheets no Drive de cada Spot. O dashboard "Padrão Spot" tem hoje duas abas ativas (Lógica & Regras, Tipologias por Spot) e uma terceira **desabilitada**: "Orçamento — em breve" (`index.html:23`).

Este design dá vida a essa aba. **A entrega principal da Fase 2 é a skill funcionando no Claude e gerando os Sheets no Drive** — isso não muda. O dashboard é a vitrine para os avaliadores entenderem e visualizarem a ideia.

---

## Objetivo

Habilitar a aba "Orçamento" no dashboard, mostrando — por empreendimento — o custo estimado de decor por tipologia, com links para os memoriais completos no Drive. Segue o mesmo padrão visual e de dados da aba "Tipologias por Spot".

---

## Decisões (do brainstorming)

| Decisão | Escolha |
|---|---|
| Data flow | Híbrido: resumo embutido no dashboard + link pro Drive |
| O que o resumo mostra | Só custo por tipologia (sem total do empreendimento) |
| Estrutura da aba | Espelhar a aba Tipologias (hero + "como gerar" + busca + cards) |
| Links pro Drive | Os dois: consolidado no topo do card + memorial por tipologia em cada linha |
| Arquitetura de dados | Arquivo `orcamentos.js` separado (`window.ORCAMENTOS`), próprio da skill orcamento-decor |

---

## Arquitetura de dados

Novo arquivo `dashboard/data/orcamentos.js`, paralelo a `tipologias.js`, reescrito pela skill `orcamento-decor`. **Não toca `tipologias.js`.**

```javascript
// dashboard/data/orcamentos.js — reescrito pela skill orcamento-decor.
window.ORCAMENTOS = {
  index: [
    {
      spot: "Natal Spot", codigo: "6953", slug: "natal-spot",
      estilo: "Clean", pacote: "Plus", gerado_em: "2026-05-27",
      total_tipologias: 5,
      consolidado_url: "https://docs.google.com/spreadsheets/d/.../edit"
    }
  ],
  spots: {
    "natal-spot": {
      spot: "Natal Spot", estilo: "Clean", pacote: "Plus",
      consolidado_url: "https://docs.google.com/spreadsheets/d/.../edit",
      tipologias: [
        {
          tipologia: "A",
          descricao: "Sem · Padrão · Cap. 2",
          custo: 41766.00,
          memorial_url: "https://docs.google.com/spreadsheets/d/.../edit"
        }
      ]
    }
  }
};
```

- `custo`: número puro (o `total_geral` do memorial). A página formata como `R$ 41.766,00`.
- `memorial_url`: Sheet individual da tipologia.
- `consolidado_url`: Sheet "Tipologias + Custo".
- Estado inicial: arquivo commitado com `index: []` e `spots: {}` vazios, para a aba carregar mostrando o empty state antes de qualquer orçamento.

---

## UI — estrutura da aba (espelha Tipologias)

### HTML (`#panel-orcamento`, novo `<main>` em `index.html`)

- Habilitar a aba: trocar o `<button class="tab is-soon" disabled>` por `<button class="tab" data-tab="orcamento">Orçamento</button>`.
- **Hero**: eyebrow "Orçamento de decor · Lançamentos" + título + lede.
- **Bloco "como gerar"**: explica a skill `orcamento-decor`; comando copiável `gera o orçamento do <empreendimento>` (ou `/orcamento-decor`). Reaproveita o padrão `.cmd-row` + botão copiar da aba Tipologias.
- **Busca**: `<input id="orc-search">` que filtra por nome/código.
- **Lista**: `<div id="orc-list">` + `<div id="orc-empty" hidden>`.

### Card de orçamento

```
┌─────────────────────────────────────────────────┐
│ Natal Spot  6953            [chip: Clean · Plus]  │
│ 5 tipologias · gerado em 2026-05-27               │
│                                                    │
│ [Ver custos]   [Abrir consolidado no Drive ↗]     │
│                                                    │
│ ▼ (ao expandir "Ver custos")                      │
│  Tipologia │ Descrição        │ Custo        │     │
│  A         │ Sem·Padrão·Cap.2 │ R$ 41.766,00 │ Memorial ↗ │
│  B         │ ...              │ ...          │ ... │
└─────────────────────────────────────────────────┘
```

- Chip de estilo + pacote (reaproveita o visual de `.fonte-tag`).
- "Ver custos" expande/colapsa a tabela (mesmo padrão de "Ver tabela" da aba Tipologias: lazy render no primeiro clique via `dataset.loaded`).
- "Abrir consolidado no Drive" → `consolidado_url`.
- Cada linha: coluna final "Memorial ↗" → `memorial_url` da tipologia.
- Custo formatado em `R$` na renderização (helper local; não embute formatação no dado).

### Empty state

Quando não há orçamento para o termo buscado (ou nenhum gerado ainda): "Nenhum orçamento gerado para X" + comando copiável `gera o orçamento do X`. Espelha o `semMatch()` da aba Tipologias.

### JS (`app.js`)

Nova IIFE separada, lê `window.ORCAMENTOS`, sem tocar na IIFE de tipologias nem na de Lógica. A navegação por abas (IIFE existente) ganha `orcamento` no objeto `panels`.

### CSS (`styles.css`)

Reaproveita classes existentes (`spot-card`, `spot-card-top`, `spot-actions`, `btn`, `btn-primary`, `btn-ghost`, `matriz`, `table-wrap`, `fonte-tag`, `cmd-row`, `spot-empty`). Adicionar só o mínimo necessário (ex: chip de estilo, coluna de link na tabela) — sem reescrever o que já existe.

---

## Mudança na skill `orcamento-decor`

O passo 8 do `SKILL.md` hoje atualiza `tipologias.js` com `estilo`/`orcamento_url`. Trocar por:

- A skill passa a **escrever/reescrever `dashboard/data/orcamentos.js`**: adiciona/atualiza o spot no `index` e em `spots`, com `estilo`, `pacote: "Plus"`, `consolidado_url`, e a lista de tipologias (`{tipologia, descricao, custo, memorial_url}`).
- O fluxo captura os `memorial_url` (um por Sheet de tipologia criado no passo 6) e o `consolidado_url` (Sheet do passo 7).
- `montar_orcamento.py` já produz `total_geral` por tipologia → vira o `custo`.
- Commit do `orcamentos.js`.
- **Não toca `tipologias.js`.**

---

## Testes / Verificação

O dashboard é estático e não tem suíte automatizada (Fases 1 e 2 testaram só os scripts Python). Verificação **manual no browser**:

1. `python -m http.server` na pasta `dashboard/`.
2. Abrir a aba Orçamento; conferir render com um `orcamentos.js` de exemplo (Natal Spot, 5 tipologias).
3. Busca filtra por nome e código.
4. "Ver custos" expande/colapsa; lazy render no primeiro clique.
5. Links: consolidado e memorial por tipologia abrem em nova aba.
6. Custo formatado corretamente (`R$ 41.766,00`).
7. Empty state com comando copiável (limpar `orcamentos.js` ou buscar termo inexistente).
8. Responsivo (mobile) e dark mode se aplicável.

Sem testes automatizados novos — coerente com o resto do dashboard.

---

## O que NÃO está no escopo

- Total do empreendimento (custo × nº de unidades) — decidido: só custo por tipologia.
- Memorial completo (itens/qtd/preços) embutido na página — fica nos Sheets do Drive.
- Fetch dos Sheets em runtime — dados são embutidos via `orcamentos.js`.
- Qualquer alteração na aba Tipologias por Spot ou no `tipologias.js`.
- Testes automatizados para o frontend.
