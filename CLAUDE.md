# hackathon-investimentos

## Herda de
Este projeto segue ~/Claude/.claude/CLAUDE.md (global) + ~/Claude/seazone/CLAUDE.md (workspace Seazone). Regras especificas dele entram aqui.

## O que faz
Hackathon SZI (IA First Investimentos), trilha Decor. Ferramentas pro time de Lancamentos/Interiores a partir do anteprojeto dos empreendimentos Spot:
1. **Skill `tabela-tipologias`** — puxa o anteprojeto LANCAMENTOS do Drive, avalia cada unidade de todos os pavimentos, classifica (Terraco + Tipo + Capacidade) e agrupa em tipologias, gerando um Google Sheet editavel.
2. **Dashboard "Padrao Spot"** — site estatico (abas: Logica & Regras · Tipologias por Spot · Orcamento) com a logica das tipologias + regras de mobiliario (programa de 13 itens, matriz de capacidade, regras de posicionamento, passo a passo de layout). Documenta o que so estava na cabeca da Raquel.
3. **Skill `orcamento-decor` (Fase 2 — FEITA)** — dado um Spot com tipologias geradas, monta o memorial descritivo de decor por tipologia (pacote **Plus**; estilo Clean/Biofilico/Industrial/Bruma) com precos do catalogo, cria Sheet(s) no Drive e alimenta a aba Orcamento (`dashboard/data/orcamentos.js`).

## Stack
- **Skills**: Python 3.12 stdlib (`csv`, `json`, `argparse`). `tabela-tipologias`: helper `montar_tabela.py`. `orcamento-decor`: `modelos.py` · `ler_catalogo.py` · `montar_orcamento.py` · `gerar_dashboard_js.py`. Testes em pytest (TDD) — suite total **71 passed**. Scripts forcam `sys.stdout.reconfigure(encoding="utf-8")` (Windows escreve cp1252 em stdout redirecionado e corrompe acentos).
- **Dashboard**: HTML/CSS/JS estatico (sem framework), dados em JS. Dev server: `python -m http.server`.
- **Identidade visual**: BrandBook Seazone — Helvetica, azul `#0054FC`, navy `#000C3C`, coral `#F06054`. Ver `docs/identidade-visual-seazone.md`.
- **Leitura de DWG** (sinal de agrupamento): ODA File Converter (DWG->DXF) + `ezdxf`. `ler_dwg.py` usa NEAREST-LABEL (bloco de esquadria mais proximo do numero da unidade) + normalizacao. Nomes de layer VARIAM por projeto (defaults AIA/Revit `A-GLAZ`/`A-AREA-IDEN` nao sao universais) — inspecionar com `--listar-layers` e adaptar. A janela e UM sinal, nao universal: TODO pavimento pode diferir/abrir por porta; avaliar piso a piso. Ver `references/arquitetura-dwg.md` e `dwg-leitura.md`.
- **Skill instalada**: copia em `~/Claude/.claude/skills/tabela-tipologias/` (descobrivel global). O repo e a fonte; recopiar pra atualizar a instalada.

## Integracoes (MCPs)
- **Google Drive** (composio) — CONECTADO, mas **autenticado como `rachel.souto@seazone.com.br`**, NAO raquel.tavares. Arquivos criados saem como owner rachel.souto; pra sair como raquel, ela precisa reconectar o conector. Este MCP **nao tem ferramenta de delete**. Le anteprojetos, cria planilha via conversao CSV->Sheet; multi-aba via upload de `.xlsx` (openpyxl) convertido.
- **Google Sheets** (composio) — NAO conectado. Planilha criada via Drive (`GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` / upload xlsx). Ver memory.md.
- GitHub.

## Regras locais (criticas)
- **Anteprojeto**: usar SEMPRE a ultima versao **LANCAMENTOS**, NUNCA "COMPATIBILIZADO INTERIORES". Caminho: `[Spot] / 02 - Projetos / 05 - Projeto Arquitetonico / 03 - Anteprojeto / [versao LANCAMENTOS]`.
- **Capacidade**: deduzir SEMPRE pela area INTERNA (privativa coberta) via Matriz de Capacidade. NUNCA contar sacada/varanda/terraco. NUNCA confiar na coluna CAPACIDADE do ANALISE.xlsx.
- **Agrupamento**: o LAYOUT/desenho manda, nao a metrica. Unidades com MESMA area+terraco+tipo+capacidade podem ser tipologias DISTINTAS (esquinas, espelhamentos) — separar conferindo a planta; nao fundir por area igual. Quando planta e area discordam, a planta vence.
- **Tipo**: PADRAO e o default. So marcar **PCD** quando confirmado na tabela final da Raquel — nao inferir de rotulo de planta sozinho.
- **Tabela de saida**: colunas TIPOLOGIA · N DAS UNIDADES (todas, sem abreviar) · TERRACO · TIPO · QUANTIDADE · CAPACIDADE (previsao) · AREA UTIL · AREA DA UNIDADE; rodape numa linha com totais; aviso de que capacidade e previsao.
- **Destino no Drive (por tipo de arquivo)**: tabela de **tipologias** -> `10 - Projeto de Interiores / 02 - Imagens`. **Memorial descritivo de decor** -> `10 - Projeto de Interiores / 03 - Memorial descritivo`. Nao sobrescrever nada.
- **Memorial descritivo**: UM unico Google Sheet com uma **aba por tipologia** (+ aba Resumo). Pacote sempre **Plus**. Custo e ESTIMATIVA (preco de referencia ou catalogo db002) — a Raquel revisa/ajusta.
- **Dashboard**: ferramenta interna fica na paleta principal (sem os verdes/amarelos de marketing).

## Estrutura / branches
- `feat/tabela-tipologias` — a skill (`skills/tabela-tipologias/`, `tests/`).
- `feat/dashboard-padrao-spot` — o dashboard (`dashboard/`).
- `docs/superpowers/` — spec e plano. `docs/identidade-visual-seazone.md` — marca.
- Validacao de referencia: Natal Spot = 5 tip / 96 un; Bonito Spot = 6 tip / 53 un; Novo Campeche Spot II = 12 tip / 49 un.
- Repo no GitHub (publico): https://github.com/raqueltavares-commits/hackathon-investimentos (`master`).

## Os 4 arquivos de base
`CLAUDE.md` (este, manual) · `memory.md` (decisoes/estado) · `lessons.md` (erros a nao repetir) · `rules.md` (estilo/convencoes).
