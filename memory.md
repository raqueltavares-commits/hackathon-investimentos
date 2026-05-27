# memory.md --- hackathon-investimentos

Decisoes arquiteturais, estado atual, links uteis.
Eu anexo automaticamente quando voce decidir algo ("vamos com X").

---

## >>> ESTADO ATUAL (2026-05-27, noite) — leia isto primeiro

**FASE 2 ENTREGUE + memorial estruturado.** Suite: **83 passed**. Aba Orcamento no ar com alert-bar "Em construcao".

**MEMORIAL ESTRUTURADO:** skill gera SOZINHA no formato oficial da Raquel: 12 colunas, 4 linhas por item, TOTAL por categoria, Taxa Decor + Taxa Adm, headline SEM jacuzzi. Scripts: `acabamentos.py`, `servicos.py`, `gerar_xlsx.py` (multi-aba), `montar_orcamento.py` (serializar_estruturado).

### Feito 2026-05-27 noite:
- 7 Google Sheets criados na pasta `03 - Memorial descritivo` do Bonito (`1n8j1M74BfZuQKva7UiqKIwxdc-JydbB5`), owner=raquel.tavares:
  - Resumo: `16xSVLo7rrrr9qblGb7tCTlW2u3ZHQ1WBphHLSAIPTZI`
  - A: `15kvKMBc_7lwJ02id_PGYLVjuh0nWGyAQAlo2qum3tU0`
  - B: `1rVGoPLb4-2NJO1Di4hs9UL6ly1kM5adN7Odu7cQEqXg`
  - C: `1YShLfXgTCoX7U7PM44-kiyxkJHZN-k6qbINnqti15MA`
  - D: `1nvv6_xn08aQB2ADzmCAUb1JPdGv9XgIQfitHiCtmMy4`
  - E: `1d1DTxxwgX5Db_bBQRCaqyxP6ScUxkQ3k8Qe0L7MVHP4`
  - F: `1lGl6b2Ugw23Z1j_cFLTCBgvfq9mMT5JBCtAws4NP0JY`
- orcamentos.js: consolidado_url novo + custos reais (A=R$44.828,67 / B+C=R$50.492,23 / D+E+F=R$44.828,67)
- Dashboard: alert-bar coral + chip "Em construcao" + GitHub push `783a68f`

**PENDENTE:**
1. Popular os 7 Sheets com dados reais (GOOGLESHEETS_UPDATE_VALUES_BATCH)
2. Retirar `em_construcao:true` do Bonito apos popular
3. Apagar os 4 Sheets errados na `02 - Imagens` (owner rachel.souto; Raquel manda pra lixeira): `1jVKKo4wnauDk4-aTd3njIY8m8dsAnSBvWiUp6NMdMrw`, `1dA-TxfWsRGINpyxSuPFImmGnMhnmbR7l7U9z0CbTM3c`, `1e3_4GtP3r6k0QFfI4U0zhOHjTicysq0WZVuooNI9Ww8`, `1Rc0ncLXkYMCBWFjvVpXwFgugUr25e8XJWJaxnkbfQYA`

**Catalogo precos:** export CSV traz so a 1a aba. Precisa da aba `db002_produtos` exportada como CSV.

---

## Decisoes Fase 2 (Arquitetura)
- Memorial no Drive: pasta **`03 - Memorial descritivo`** (`1n8j1M74BfZuQKva7UiqKIwxdc-JydbB5`)
- Formato: **UM Sheet por tipologia** (+ Resumo) — Sheets SEPARADOS via `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` (CSV->Sheet) + `GOOGLESHEETS_UPDATE_VALUES_BATCH`
- Multi-aba via xlsx NAO funciona na pratica (Drive converte em 1 aba; base64 nao chega no sandbox)
- Scripts forcam `sys.stdout.reconfigure(encoding=utf-8)` — Windows cp1252 corrompia acentos
- Custo = numero puro; pagina formata em R$
- Regra "Garden=jacuzzi" NAO universal: no Bonito so 113 tem jacuzzi

---

## Como rodar
**Suite:** `python -m pytest tests/ -q` (esperado: 83 passed)
**Dashboard:** `python -m http.server 5500 --directory dashboard` (abrir http://localhost:5500)
**Pasta:** `C:\Users\Seazone\Claude\seazone\hackathon-investimentos`

---

## Composio (MCP Drive/Sheets)
- Status: conectado como `raquel.tavares@seazone.com.br`
- Instavel: fecha/abres `/mcp` ate reconectar
- Sheets precisa de OAuth separado (autorizar quando solicitado)
- Criar Sheet: `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` (mime=`application/vnd.google-apps.spreadsheet`, content=CSV)
- Popular: `GOOGLESHEETS_UPDATE_VALUES_BATCH` (sheetId via GET_SHEET_NAMES)

---

## Validacao de referencia
- Natal Spot = 5 tip / 96 un
- Bonito Spot = 6 tip / 53 un
- Novo Campeche Spot II = 12 tip / 49 un

## GitHub
Repo: https://github.com/raqueltavares-commits/hackathon-investimentos
Branch: `master`
