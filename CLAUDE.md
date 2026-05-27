# hackathon-investimentos

## Herda de
Este projeto segue ~/Claude/.claude/CLAUDE.md (global) + ~/Claude/seazone/CLAUDE.md (workspace Seazone). Regras especificas dele entram aqui.

## O que faz
Hackathon SZI (IA First Investimentos), trilha Decor. Ferramentas pro time de Lancamentos/Interiores a partir do anteprojeto dos empreendimentos Spot:
1. **Skill `tabela-tipologias`** — puxa o anteprojeto LANCAMENTOS do Drive, avalia cada unidade de todos os pavimentos, classifica (Terraco + Tipo + Capacidade) e agrupa em tipologias, gerando um Google Sheet editavel.
2. **Dashboard "Padrao Spot"** — site estatico com a logica das tipologias + regras de mobiliario (programa de 13 itens, matriz de capacidade, regras de posicionamento, passo a passo de layout). Documenta o que so estava na cabeca da Raquel.
3. **Fase 2 (a fazer)** — orcamento preliminar do decor puxando do catalogo.

## Stack
- **Skill**: Python 3.12 stdlib (`csv`, `json`); helper `montar_tabela.py`. Testes em pytest (TDD).
- **Dashboard**: HTML/CSS/JS estatico (sem framework), dados em JS. Dev server: `python -m http.server`.
- **Identidade visual**: BrandBook Seazone — Helvetica, azul `#0054FC`, navy `#000C3C`, coral `#F06054`. Ver `docs/identidade-visual-seazone.md`.
- **Leitura de DWG** (fonte mais precisa): ODA File Converter (DWG->DXF) + `ezdxf`. Esquadrias no layer `A-GLAZ`. Ver `skills/tabela-tipologias/references/dwg-leitura.md`.

## Integracoes (MCPs)
- **Google Drive** (composio) — CONECTADO. Le anteprojetos, cria a planilha (via conversao CSV->Sheet).
- **Google Sheets** (composio) — NAO conectado. Por isso a planilha e criada via Drive (`GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` com mime spreadsheet). Ver memory.md.
- GitHub.

## Regras locais (criticas)
- **Anteprojeto**: usar SEMPRE a ultima versao **LANCAMENTOS**, NUNCA "COMPATIBILIZADO INTERIORES". Caminho: `[Spot] / 02 - Projetos / 05 - Projeto Arquitetonico / 03 - Anteprojeto / [versao LANCAMENTOS]`.
- **Capacidade**: deduzir SEMPRE pela area INTERNA (privativa coberta) via Matriz de Capacidade. NUNCA contar sacada/varanda/terraco. NUNCA confiar na coluna CAPACIDADE do ANALISE.xlsx.
- **Agrupamento**: mesma area interna + terraco + tipo = mesma tipologia (tolera diferenca pequena de m2); diferenca grande de m2 = layouts distintos = tipologias separadas.
- **Tabela de saida**: colunas TIPOLOGIA · N DAS UNIDADES (todas, sem abreviar) · TERRACO · TIPO · QUANTIDADE · CAPACIDADE (previsao) · AREA UTIL · AREA DA UNIDADE; rodape numa linha com totais; aviso de que capacidade e previsao.
- **Destino da planilha no Drive**: `05 - Projeto Arquitetonico / 10 - Projeto de Interiores / 02 - Imagens` do proprio Spot. Nao sobrescrever nada.
- **Dashboard**: ferramenta interna fica na paleta principal (sem os verdes/amarelos de marketing).

## Estrutura / branches
- `feat/tabela-tipologias` — a skill (`skills/tabela-tipologias/`, `tests/`).
- `feat/dashboard-padrao-spot` — o dashboard (`dashboard/`).
- `docs/superpowers/` — spec e plano. `docs/identidade-visual-seazone.md` — marca.
- Validacao de referencia: Natal Spot = 5 tipologias / 96 unidades.

## Os 4 arquivos de base
`CLAUDE.md` (este, manual) · `memory.md` (decisoes/estado) · `lessons.md` (erros a nao repetir) · `rules.md` (estilo/convencoes).
