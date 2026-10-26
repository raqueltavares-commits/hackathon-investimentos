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
1. `mcp__drive-raquel__GOOGLEDRIVE_FIND_FILE` na raiz `1D9y8aKfkGGE13WbGMlw07G8Euu0Pg7fF` → ache a pasta do Spot.
2. Desça `02 - Projetos` → `05 - Projeto Arquitetônico` → `03 - Anteprojeto`.
3. Escolha a última versão **LANÇAMENTOS** (NUNCA COMPATIBILIZADO INTERIORES).
4. Pegue o `ANÁLISE_..._V0X.xlsx` (preferência) e/ou o `LANÇAMENTO_AP_..._V0X.pdf`.

### 2. Levantar as unidades (todos os pavimentos)
**FONTE IDEAL = DWG + PDF (cruzar os dois).** Cada um dá uma parte:
- **PDF** (ou `ANÁLISE.xlsx`): **metragem por unidade**, **nº/total de unidades**, quadro
  de áreas e textos relevantes. → os NÚMEROS e o texto.
- **DWG**: **esquadrias** (layer `A-GLAZ`), portas, layout, espelhamento. → o AGRUPAMENTO
  (diferencia unidades de mesma área que diferem só pela janela de esquina).

Passos: do PDF/planilha tire área interna (privativa coberta), área da unidade (total),
terraço e o total de unidades. Sempre validar o total de unidades entre as fontes.

**Leitura DWG (automática) — quando houver DWG no Drive:**
Na pasta do anteprojeto LANÇAMENTOS costuma haver uma subpasta `DWG` (uma planta por
pavimento). Baixe o(s) DWG dos pavimentos de unidades do Drive:
`mcp__drive-raquel__GOOGLEDRIVE_FIND_FILE` (`q: "'<id da pasta DWG>' in parents and trashed=false"`) →
`mcp__drive-raquel__GOOGLEDRIVE_DOWNLOAD_FILE(fileId)` (devolve URL temporária) →
`curl -s -o <scratchpad>/pavimento.dwg "<url>"`. Então, **para cada pavimento**:

1. **Inspecione os layers primeiro** (os nomes VARIAM de projeto pra projeto — desenhistas
   diferentes nomeiam diferente; os defaults seguem AIA/Revit mas não são universais):
   ```bash
   py -3 <SKILL_DIR>/scripts/unidades_dwg.py --dwg caminho/pavimento.dwg --listar-layers
   ```
   Identifique o layer dos **números de unidade** e o(s) de **esquadria**.
2. **Conte as janelas por unidade** (passe os layers do projeto se diferirem dos defaults):
   ```bash
   py -3 <SKILL_DIR>/scripts/unidades_dwg.py --dwg caminho/pavimento.dwg \
     --label-layer A-AREA-IDEN --janela-layers A-GLAZ,A-GLAZ-IDEN
   ```
   Retorna `{unidade: nº de janelas}` (normalizado). Unidades com nº diferente = tipologias
   diferentes (a de esquina tem +1). Detalhes em `references/arquitetura-dwg.md`.

⚠️ **A janela é UM sinal, não o único nem universal.** QUALQUER pavimento (térreo, tipo,
rooftop) pode ter unidades diferentes (PCD, garden, layout próprio) e pode abrir por **porta**
em vez de janela → aí a contagem vem ~0 e o agrupamento sai da **ÁREA** (PDF) + layout. Avalie
**pavimento a pavimento**; nunca assuma qual sinal vale onde — depende do projeto. NUNCA exclua
um pavimento do agrupamento.

Sem DWG (ou pra confirmar), **renderize e olhe as PLANTAS do PDF** (`fitz`, dpi ~170) — a
planilha sozinha NÃO dá o layout: metragem parecida pode ser tipologia diferente.

### 2c. Validação via Revit (OPCIONAL — complemento, não fonte)
Se o **Revit do Spot estiver aberto** (MCP **Revit-SZI** ativo — `mcp__Revit-SZI__get_revit_status`;
se as tools não aparecerem, ToolSearch `"+Revit-SZI"`), use-o como 2ª/3ª opinião. NUNCA
substitui o anteprojeto LANÇAMENTOS (a fonte da tabela); **só sinaliza divergências** pra
Raquel decidir. Sem Revit, pule este passo.

1. `mcp__Revit-SZI__get_current_view_info` → confirme o modelo do Spot; níveis em `mcp__Revit-SZI__list_levels`.
2. **Rooms:** `mcp__Revit-SZI__export_room_data` (devolve number/name/level/area_sqm de todas as Rooms;
   filtre pelos níveis de unidades). **Esquadrias:** conte **janelas** e portas por unidade com
   `mcp__Revit-SZI__ai_element_filter(category="OST_Windows"|"OST_Doors", max_elements=2000)` (parâmetro =
   nome do BuiltInCategory) e, por elemento, `mcp__Revit-SZI__get_element_properties(element_id)` para
   host/FromRoom/ToRoom. Se a Room não vier nos parâmetros, use `mcp__Revit-SZI__execute_revit_code`
   (IronPython, SÓ LEITURA, sem Transaction) lendo `inst.FromRoom`/`inst.ToRoom`/`inst.Room` da fase final
   (porta = from/to room; janela = host wall que limita a Room — NEAREST-ROOM). Monte
   `tmp/revit.json` = `{"unidades":[{"unidade":"101","area_revit":16.84,"janelas":2,"portas":1}]}`.
   (Janela é o sinal principal; porta é apoio. Se não der pra contar janela com confiança, omita.)
3. Rode a validação (depois de ter a classificação do passo 3 em `unidades.json`):
   ```bash
   py -3 <SKILL_DIR>/scripts/validar_revit.py --unidades unidades.json --revit tmp/revit.json --tol 0.5
   ```
   Devolve `validacoes` (área/capacidade por unidade), `contagem`, `sem_match_*`,
   `esquadrias_por_grupo` e `divergencias`. **Tolerância de área = 0,5 m²**. A capacidade pela
   área do Revit é comparada com a classificada. **Esquadrias:** dentro de cada grupo
   (terraço+tipo+capacidade+área) o nº de janelas diferente sinaliza **possível tipologia
   separada** (ex.: esquina) — reforça o A-GLAZ do DWG.
4. **Toda divergência vai pro resumo executivo (passo 5.4)** — a Raquel decide; a tabela sai
   pelo anteprojeto.

### 3. Classificar cada unidade
Leia `references/classificacao-spot.md`. Para cada unidade derive:
`terraco`, `tipo`, `capacidade` (PREVISÃO), `area_util`, `area_unidade`.
**Capacidade:** deduza SEMPRE pela **área interna** (privativa coberta), aplicando a
Matriz — **nunca** conte a área de sacada/varanda/terraço, e **não** use a coluna
CAPACIDADE do ANÁLISE (vem errada). Unidades com mesma área interna têm a mesma
capacidade, com ou sem sacada. `area_util` = privativa coberta; `area_unidade` = total.
Monte uma lista JSON no contrato do helper:
```json
[{"unidade":"101","pavimento":1,"terraco":"Sem","tipo":"Padrão",
  "capacidade":2,"area_util":14.33,"area_unidade":18.50}]
```

### 4. Agrupar, validar e gerar CSV
Rode o helper (salve a lista em `unidades.json`). `<SKILL_DIR>` = a pasta deste SKILL.md:
```bash
py -3 <SKILL_DIR>/scripts/montar_tabela.py --total <TOTAL_DECLARADO> < unidades.json
# com leitura DWG integrada (separa esquinas automaticamente):
py -3 <SKILL_DIR>/scripts/montar_tabela.py --total <TOTAL_DECLARADO> --dwg caminho/pavimento.dwg < unidades.json
```
Ele retorna `tipologias`, `validacao` (soma vs total), `avisos` e `csv`. O `--dwg` separa
unidades de mesma área com nº de janelas diferente (labels pareados tipo "201-301" são
expandidos automaticamente).
**Se `validacao.ok == false`, NÃO entregue como certo — destaque a divergência.**

⚠️ O helper agrupa só por (terraço + tipo + capacidade + área) — isso é um **ponto de
partida**, NÃO a verdade. Confira contra as PLANTAS: unidades de área parecida mas
**layout diferente** (esquina, espelhamento, orientação) devem virar tipologias separadas;
faça esse ajuste antes de entregar. Marque `fonte: "analise"` só quando áreas vieram da
planilha; em qualquer caso o agrupamento por layout depende da leitura da planta.

### 5. Entregar
1. Salve o CSV em `docs/tipologias_<spot>.csv` (snapshot versionável, encoding UTF-8).
   `docs/` e `dashboard/` são do repo `C:\Users\Seazone\Claude\seazone\hackathon-investimentos`;
   qualquer alteração lá vai em **branch `feat/tipologias-<slug>` + PR pra `staging`/`dev`** (nunca direto na `main`).
2. Crie um **novo** Google Sheet no Drive **dentro de `05 - Projeto Arquitetônico /
   10 - Projeto de Interiores / 02 - Imagens`** do próprio Spot (ver `references/drive-navegacao.md`).
   Use `mcp__drive-raquel__GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` (`file_name`, `parent_id`,
   `mime_type=application/vnd.google-apps.spreadsheet`) com o CSV (+ uma linha de aviso
   de capacidade) como `text_content`. Valide exportando de volta (`mcp__drive-raquel__GOOGLEDRIVE_DOWNLOAD_FILE`
   com `mime_type=text/csv` → URL temporária → `curl`). Conta: `raquel.tavares`. NÃO sobrescreva nada. Devolva o link.
3. **Alimente a vitrine do dashboard** (SÓ no projeto `hackathon-investimentos`, se a pasta
   `dashboard/` existir): edite `dashboard/data/tipologias.js` — adicione/atualize o Spot em
   `window.TIPOLOGIAS.spots[<slug>]` (com `tipologias`, `drive_url`) e a entrada em
   `window.TIPOLOGIAS.index` (spot, codigo, slug, gerado_em, total_tipologias,
   total_unidades, drive_url, **`fontes`**). `fontes` = objeto `{ pdf, analise, dwg }` com
   `true/false` indicando quais fontes alimentaram a tabela (vira as tags verde/vermelho na
   vitrine). Inclua **`revit`** quando o passo 2c rodou. Ex.: PDF + DWG + Revit, sem planilha →
   `{ pdf: true, analise: false, dwg: true, revit: true }`.
4. Escreva um **resumo executivo** (chat): total de tipologias/unidades, resultado da
   validação, `avisos` de baixa confiança/fronteira de área, premissas da previsão de capacidade.
   **Se rodou o passo 2c, liste as `divergencias` do Revit** (área/capacidade/contagem) em
   destaque — a Raquel decide caso a caso; a tabela continua pelo anteprojeto.

## Validação de referência
Natal Spot deve dar **5 tipologias / 96 unidades** (A=74/cap2, B=10/cap5, C=10/cap3,
D=1/cap5 sacada, E=1/cap3 sacada).
