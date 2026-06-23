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

Pergunte tambem (ou use campo do entry, se existir): **tem Taxa Decor (6%)?** — guarde `TEM_DECOR` (sim/nao).

#### 1b. Endereço/CEP do empreendimento (Nekt) — pro cabeçalho e frete

Via MCP Nekt (`execute_sql`), busque endereço e CEP por `short_name`:
```sql
SELECT street_name, address_number, address_complement, neighborhood, city, state, postal_code
FROM nekt_operacional_bronze.sup_bd_szi_szi_spot_buildings
WHERE short_name = 'SPOT_NAME'  -- ex: 'Natal Spot'
```
Monte `ENDERECO` ("Rua, nº — Bairro, Cidade - UF") e `CEP` (formate 99999-999). Passa pro xlsx (passo 4). Se não achar, deixe em branco.

### 2. Ler o catálogo de preços (Supabase, ao vivo)

A base de valores agora é o app **seazone-decor-interno** (Supabase). Leia ao vivo:

```bash
python skills/orcamento-decor/scripts/fetch_catalogo.py > tmp/produtos.json
```

O script resolve a anon key do bundle de produção, consulta os produtos + serviços do
de-para (`references/depara-catalogo.json`, ~40 códigos: produtos `*` + serviços `SRV*`)
e devolve `produtos.json` com `valor_unitario`, `cor_acabamento` e `link` (= referência).
Se a rede/base falhar (sai com `{"erro": ...}` em stderr, código 1): pule e gere com os
valores default (omita `--produtos` no passo 4). Os serviços (elétrica/hidráulica/ar/
gerais/pintura/feltro/limpeza) vêm da categoria **Serviços** da base — preço pela base.

### 3. Preparar tipologias.json

Extraia de `dashboard/data/tipologias.js` -> `spots["SLUG"].tipologias` e salve em `tmp/tipologias_spot.json`.
Formato esperado:
```json
[{"tipologia":"A","terraco":"Sem","tipo":"Padrao","capacidade":2}, ...]
```

### 4. Gerar memoriais

```bash
python skills/orcamento-decor/scripts/montar_orcamento.py \
  --tipologias tmp/tipologias_spot.json \
  --produtos tmp/produtos.json \
  --estilo ESTILO \
  --spot "SPOT_NAME" > tmp/memoriais.json
# acrescente --sem-decor SE TEM_DECOR = nao (zera a Taxa Decor)
```
(Se a leitura do catálogo falhou no passo 2, omita `--produtos`.)

O JSON traz, por tipologia: `rows` (matriz de **11 colunas** no formato do novo template —
`AMBIENTE · CATEGORIA · ITEM · COR DE ACABAMENTO · FORNECEDOR · QTD · REFERÊNCIA · VALOR UNIT. ·
VALOR TOTAL · FRETE · TOTAL + FRETE`, uma linha por item, TOTAL por categoria, Taxa Decor 6% e
TOTAL GERAL), `total_geral` (SEM jacuzzi, vai pro dashboard) e `total_com_jacuzzi`.

> **Taxas:** unidades NÃO levam Taxa Adm (só área comum). Taxa Decor 6% incide nas duas; quando
> não tem, use `--sem-decor` (a linha fica zerada). **Frete:** coluna por item (default 0,
> preenchimento manual); `TOTAL + FRETE` = valor total + frete. **Serviços e instalações** entram
> embutidos dentro de cada tipologia (categoria SERVIÇOS), não em aba separada.

Gere o `.xlsx` multi-aba (uma aba por tipologia + Resumo Unidades), com cabeçalho Endereço/CEP:
```bash
python skills/orcamento-decor/scripts/gerar_xlsx.py \
  --memoriais tmp/memoriais.json --spot "SPOT_NAME" --saida tmp/Orcamento_SPOT.xlsx \
  --endereco "ENDERECO" --cep "CEP"
```

### 5. Subir o memorial no Drive (UM Sheet, abas por tipologia)

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

### 6. Atualizar a vitrine do dashboard (orcamentos.js)

Agora o memorial e UM unico Sheet (aba Resumo + uma aba por tipologia). Entao:
- `consolidado_url` = link do Sheet do passo 5 (a aba Resumo ja e o consolidado).
- `memorial_url` de cada tipologia = o MESMO link (todas as tipologias estao nesse Sheet, em abas).

Monte `tmp/memorial_urls.json` com todas as tipologias apontando pro mesmo link e rode o script (faz upsert do Spot em `dashboard/data/orcamentos.js`, sem tocar `tipologias.js`):

```bash
# tmp/memorial_urls.json -> {"A": "<link do Sheet>", "B": "<mesmo link>", ...}
python skills/orcamento-decor/scripts/gerar_dashboard_js.py \
  --orcamentos-js dashboard/data/orcamentos.js \
  --spot "SPOT_NAME" --codigo CODIGO --slug SLUG \
  --estilo ESTILO_CAPITALIZADO \
  --consolidado-url "<link do Sheet do passo 5>" \
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

### 7. Apresentar resultado

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
