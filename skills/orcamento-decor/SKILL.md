---
name: orcamento-decor
description: Gera o orcamento preliminar de decor (memorial descritivo, pacote Plus) por tipologia de um Spot, usando precos do catalogo real no Drive. Ativa com "gera o orcamento do <Spot>", "memorial de decor do <Spot>", "orcamento preliminar", /orcamento-decor.
---

# Skill: orcamento-decor

Gera memorial descritivo de decor por tipologia (pacote Plus fixo, estilo a escolher).
**NAO modifica a skill tabela-tipologias nem seus arquivos.**

## Quando usar
"gera o orcamento do <Spot>", "memorial de decor do <Spot>", "orcamento preliminar", `/orcamento-decor`.

## Procedimento

### 1. Identificar Spot e estilo

Leia `dashboard/data/tipologias.js`. Ache o spot pelo nome no `index`.
- Se o entry ja tiver campo `estilo`: use-o.
- Se nao tiver: pergunte -> "Qual o estilo deste Spot? (1) Clean  (2) Biofilico  (3) Industrial  (4) Bruma"
- Salve como `ESTILO` (ex: `clean`, `biofilico`, `industrial`, `bruma`).

Guarde tambem: `SPOT_NAME`, `SLUG`, `TIPOLOGIAS_DRIVE_URL` (campo `drive_url`).

### 2. Baixar catalogo do Drive

```
GOOGLEDRIVE_DOWNLOAD_FILE
  fileId: 1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o
  exportMimeType: text/csv
```
Salve em `tmp/db002.csv`. Se falhar por timeout/permissao: pule o passo 3 (usara precos default).

### 3. Parsear catalogo

```bash
python skills/orcamento-decor/scripts/ler_catalogo.py --csv tmp/db002.csv > tmp/produtos.json
```

Se o script falhar com "Colunas nao encontradas":
- O erro mostra as colunas disponíveis
- Consulte `skills/orcamento-decor/references/catalogo-schema.md`
- Chame novamente com `--col-<campo> <nome_real>`
- Documente o schema correto em `catalogo-schema.md` e faca commit

### 4. Preparar tipologias.json

Extraia de `dashboard/data/tipologias.js` -> `spots["SLUG"].tipologias` e salve em `tmp/tipologias_spot.json`.
Formato esperado:
```json
[{"tipologia":"A","terraco":"Sem","tipo":"Padrao","capacidade":2}, ...]
```

### 5. Gerar memoriais

```bash
python skills/orcamento-decor/scripts/montar_orcamento.py \
  --tipologias tmp/tipologias_spot.json \
  --produtos tmp/produtos.json \
  --estilo ESTILO \
  --spot "SPOT_NAME" > tmp/memoriais.json
```
(Se pulou o passo 3, omita `--produtos`.)

O JSON traz, por tipologia: `rows` (matriz de 12 colunas no formato oficial — categoria/ambiente, 4 linhas por item com ficha tecnica, TOTAL por categoria, Taxa Decor/Adm, e os dois totais), `total_geral` (SEM jacuzzi, vai pro dashboard) e `total_com_jacuzzi`.

Gere o `.xlsx` multi-aba (uma aba por tipologia + Resumo):
```bash
python skills/orcamento-decor/scripts/gerar_xlsx.py \
  --memoriais tmp/memoriais.json --spot "SPOT_NAME" --saida tmp/Orcamento_SPOT.xlsx
```

### 6. Subir o memorial no Drive (UM Sheet, abas por tipologia)

Destino: pasta **`03 - Memorial descritivo`** do Spot
(`Spot / 02 - Projetos / 05 - Projeto Arquitetonico / 10 - Projeto de Interiores / 03 - Memorial descritivo`),
NAO a `02 - Imagens` (la fica so a tabela de tipologias).

Suba o `.xlsx` como **um unico arquivo**, convertido pra Google Sheet (preserva as abas):
```
GOOGLEDRIVE_CREATE_FILE  (base64 do .xlsx)
  title: "Memorial Descritivo - SPOT_NAME (ESTILO Plus)"
  base64Content: <base64 de tmp/Orcamento_SPOT.xlsx>
  contentMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  parentId: <id da pasta 03 - Memorial descritivo>
```
O Drive converte o `.xlsx` em Google Sheet com **uma aba por tipologia** (+ Resumo). Guarde o link.

> Conta do conector: hoje o Drive (composio) autentica como `rachel.souto`. Pra o arquivo
> sair como `raquel.tavares`, reconectar o conector antes. Este MCP nao tem delete.

### 7. Atualizar a vitrine do dashboard (orcamentos.js)

Agora o memorial e UM unico Sheet (aba Resumo + uma aba por tipologia). Entao:
- `consolidado_url` = link do Sheet do passo 6 (a aba Resumo ja e o consolidado).
- `memorial_url` de cada tipologia = o MESMO link (todas as tipologias estao nesse Sheet, em abas).

Monte `tmp/memorial_urls.json` com todas as tipologias apontando pro mesmo link e rode o script (faz upsert do Spot em `dashboard/data/orcamentos.js`, sem tocar `tipologias.js`):

```bash
# tmp/memorial_urls.json -> {"A": "<link do Sheet>", "B": "<mesmo link>", ...}
python skills/orcamento-decor/scripts/gerar_dashboard_js.py \
  --orcamentos-js dashboard/data/orcamentos.js \
  --spot "SPOT_NAME" --codigo CODIGO --slug SLUG \
  --estilo ESTILO_CAPITALIZADO \
  --consolidado-url "<link do Sheet do passo 6>" \
  --memoriais tmp/memoriais.json \
  --memorial-urls tmp/memorial_urls.json \
  --gerado-em AAAA-MM-DD
```

Faca commit:
```bash
git add dashboard/data/orcamentos.js
git commit -m "feat(orcamento): vitrine do SPOT_NAME no dashboard"
```

**NUNCA edite `tipologias.js` (arquivo da skill tabela-tipologias).**

### 9. Apresentar resultado

Mostre:
```
Orcamento gerado — SPOT_NAME (ESTILO · Plus)

Tipologia | Descricao               | Custo estimado
A         | Sem · Padrao · Cap. 2   | R$ XX.XXX,XX
B         | Garden · Padrao · Cap. 4| R$ XX.XXX,XX
...

Sheets criados:
- [Tipologia A] <link>
- [Tipologia B] <link>
- ...
- [Tipologias + Custo] <link>

Precos de referencia (Plus 2026). Confirmar com catalogo atualizado.
```

## IDs do Drive

| Recurso | ID |
|---|---|
| Catalogo principal (db002_produtos) | `1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o` |
| Marcenaria por estilo | `1VnEZ-2UscCx03cwEGEDVA9vbfaUw4Y04wiM_lh9YRYI` |
| Pasta raiz estilos | `1uEBBTJlSUpOh2WxM1GRbx1e932xqI_dy` |
| Pasta estilo CLEAN | `17Nh0A_EsLt1gvwdB-9kcMtTVKkJSsX5O` |
| Pasta estilo BIOFILICO | `10HKb-ckaIp_x81LXBvEGevEwIAcmD46H` |
| Pasta estilo INDUSTRIAL | `1XFt6ucRgmmq1PGn4vNxv3tiHuVfmT5Jd` |
| Pasta estilo BRUMA | `19HSW3nsiNcpY5RZNZO4NRguHtXAGgq98` |
