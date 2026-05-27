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

### 6. Criar Sheets de orcamento no Drive

Encontre a pasta `02 - Imagens` do Spot (mesmo caminho da skill tabela-tipologias:
`Spot / 02 - Projetos / 05 - Projeto Arquitetonico / 10 - Projeto de Interiores / 02 - Imagens`).

Para CADA memorial em `tmp/memoriais.json`:
```
GOOGLEDRIVE_CREATE_FILE_FROM_TEXT
  title: "Orcamento Decor - SPOT_NAME - Tipologia LETRA (ESTILO Plus)"
  text_content: <campo "csv" do memorial>
  content_mime_type: text/csv
  parent_id: <id da pasta 02 - Imagens>
```
O Drive converte o CSV em Sheet editavel. Guarde o link retornado.

### 7. Criar Sheet tipologias + custo

Baixe o CSV do Sheet de tipologias original via Drive (use `drive_url` do spot):
```
GOOGLEDRIVE_DOWNLOAD_FILE fileId: <id> exportMimeType: text/csv
```

Adicione coluna `CUSTO ESTIMADO DECOR (Plus ESTILO)` com o `total_geral` de cada tipologia.
Crie novo Sheet:
```
GOOGLEDRIVE_CREATE_FILE_FROM_TEXT
  title: "SPOT_NAME - Tipologias + Custo Plus ESTILO"
  text_content: <CSV original com coluna extra>
  content_mime_type: text/csv
  parent_id: <id da pasta 02 - Imagens>
```

### 8. Atualizar tipologias.js

Se o spot nao tinha `estilo`, adicione ao entry do index:
```javascript
estilo: "ESTILO",
orcamento_url: "<link do Sheet tipologias+custo>"
```
Faca commit:
```bash
git add dashboard/data/tipologias.js
git commit -m "feat(orcamento): estilo e orcamento_url do SPOT_NAME"
```

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
