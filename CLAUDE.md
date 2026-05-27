# hackathon-investimentos

## Herda de
Este projeto segue ~/Claude/.claude/CLAUDE.md (global) + ~/Claude/seazone/CLAUDE.md (workspace Seazone). Regras especificas dele entram aqui.

## O que faz
Hackathon SZI (IA First Investimentos), trilha Decor. Ferramentas pro time de Lancamentos/Interiores a partir do anteprojeto dos empreendimentos Spot:
1. **Skill `tabela-tipologias`** — puxa o anteprojeto LANCAMENTOS do Drive, avalia cada unidade de todos os pavimentos, classifica (Terraco + Tipo + Capacidade) e agrupa em tipologias, gerando um Google Sheet editavel.
2. **Dashboard "Padrao Spot"** — site estatico (abas: Logica & Regras · Tipologias por Spot · Orcamento) com a logica das tipologias + regras de mobiliario + orcamentos por Spot.
3. **Skill `orcamento-decor` (Fase 2 — ENTREGUE)** — dado um Spot com tipologias geradas, monta o memorial descritivo de decor por tipologia (pacote **Plus**; estilo Clean/Biofilico/Industrial/Bruma) com precos do catalogo, cria Google Sheets no Drive e alimenta a aba Orcamento.

## Stack
- **Skills**: Python 3.12 stdlib (`csv`, `json`, `argparse`, `openpyxl`). `tabela-tipologias`: `montar_tabela.py`. `orcamento-decor`: `modelos.py` · `ler_catalogo.py` · `acabamentos.py` · `servicos.py` · `montar_orcamento.py` · `gerar_xlsx.py` · `gerar_dashboard_js.py`. Testes em pytest — suite total **83 passed**.
- **Dashboard**: HTML/CSS/JS estatico (sem framework), dados em JS. Dev server: `python -m http.server 5500 --directory dashboard` (abrir http://localhost:5500).
- **Identidade visual**: BrandBook Seazone — Helvetica, azul `#0054FC`, navy `#000C3C`, coral `#F06054`.
- **Leitura de DWG**: ODA File Converter (DWG->DXF) + `ezdxf`. `ler_dwg.py` usa NEAREST-LABEL + normalizacao. Layers CONFIGURAVEIS — variar por projeto. Ver `skills/tabela-tipologias/references/dwg-leitura.md`.
- **Skills instaladas**: copiadas em `~/Claude/.claude/skills/tabela-tipologias/` e `~/Claude/.claude/skills/orcamento-decor/`. O repo e a fonte; recopiar pra atualizar.

## Integracoes (MCPs)
- **Google Drive + Sheets** (composio) — conectados como `raquel.tavares@seazone.com.br`. Upload via `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` (CSV->Sheet conversion). Atualizar celulas via `GOOGLESHEETS_UPDATE_VALUES_BATCH`.
- Composio as vezes para de responder mesmo mostrando "Connected" — fechar/abrir aba MCP resolve.
- **GitHub**: repo publico https://github.com/raqueltavares-commits/hackathon-investimentos, branch `master`.

## Regras locais (criticas)
- **Anteprojeto**: usar SEMPRE a ultima versao **LANCAMENTOS**, NUNCA "COMPATIBILIZADO INTERIORES".
- **Capacidade**: deduzir pela area INTERNA (privativa coberta). <=17m2=cap2, ~18=cap3, ~19-21=cap4, >=22=cap5. PCD rende -1 nivel. NUNCA contar sacada/varanda/terraco.
- **Agrupamento**: o LAYOUT/desenho manda, nao a metrica. Esquinas sao tipologia propria. Planta vence area.
- **Tipo**: PADRAO e default. So marcar PCD quando confirmado.
- **Tabela de saida**: TIPOLOGIA · N DAS UNIDADES (todas, sem abreviar) · TERRACO · TIPO · QUANTIDADE · CAPACIDADE (previsao) · AREA UTIL · AREA DA UNIDADE.
- **Destino no Drive**: tipologias -> `02 - Imagens`. Memorial decor -> `03 - Memorial descritivo`. NAO sobrescrever.
- **Memorial**: UM Google Sheet com ABA por tipologia (+ aba Resumo). Pacote sempre Plus. Custo = ESTIMATIVA — a Raquel revisa.

## Validacao de referencia
- Natal Spot = 5 tip / 96 un
- Bonito Spot = 6 tip / 53 un
- Novo Campeche Spot II = 12 tip / 49 un

## Estrutura
- `skills/tabela-tipologias/` — skill de tipologias
- `skills/orcamento-decor/` — skill de orcamento (Fase 2)
- `dashboard/` — site estatico com 3 abas
- `docs/superpowers/` — specs e planos
- `tests/` — suite pytest (83 tests)

## Os 4 arquivos de base
`CLAUDE.md` (este, manual) · `memory.md` (decisoes/estado) · `lessons.md` (erros a nao repetir) · `rules.md` (estilo/convencoes).
