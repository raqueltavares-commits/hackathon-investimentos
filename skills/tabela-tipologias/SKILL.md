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
Enumere TODAS as unidades com: número, pavimento, **área interna (privativa coberta)**,
área da unidade (privativa total), terraço. Use o ANÁLISE só para as **áreas**.

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
Rode o helper (salve a lista em `unidades.json`):
```bash
python skills/tabela-tipologias/scripts/montar_tabela.py --total <TOTAL_DECLARADO> < unidades.json
```
Ele retorna `tipologias`, `validacao` (soma vs total), `avisos` e `csv`.
**Se `validacao.ok == false`, NÃO entregue como certo — destaque a divergência.**

### 5. Entregar
1. Salve o CSV em `docs/tipologias_<spot>.csv` (snapshot versionável, encoding UTF-8).
2. Crie um **novo** Google Sheet no Drive (`GOOGLESHEETS_CREATE_GOOGLE_SHEET1` + escrita
   de valores) **dentro de `05 - Projeto Arquitetônico / 10 - Projeto de Interiores / 02 - Imagens`**
   do próprio Spot (ver `references/drive-navegacao.md`). NÃO sobrescreva planilhas
   existentes. Devolva o link.
3. Coloque na planilha a nota fixa de capacidade:
   "⚠️ Capacidade é previsão baseada em área útil + programa — confirmar/editar
   quando o layout final estiver pronto."
4. Escreva um **resumo executivo** (chat + opcional no Sheet): total de tipologias/
   unidades, resultado da validação, `avisos` de baixa confiança/fronteira de área,
   premissas usadas na previsão de capacidade.

## Validação de referência
Natal Spot deve dar **5 tipologias / 96 unidades** (A=74/cap2, B=10/cap5, C=10/cap3,
D=1/cap5 sacada, E=1/cap3 sacada).
