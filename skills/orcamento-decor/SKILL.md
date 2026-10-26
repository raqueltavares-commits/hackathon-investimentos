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

> **Onde rodar (Claude Code):** `SKILL_DIR = C:\Users\Seazone\Claude\.claude\skills\orcamento-decor`.
> `dashboard/` e `tmp/` são do repo `C:\Users\Seazone\Claude\seazone\hackathon-investimentos` —
> rode os comandos com esse repo como pasta atual e antes defina no Bash:
> `SKILL_DIR="C:/Users/Seazone/Claude/.claude/skills/orcamento-decor"` (os scripts rodam da skill global;
> a cópia em `hackathon-investimentos/skills/` é espelho).
> A cópia em `projetos\interiores-lancamentos\skills\orcamento-decor` é ANTIGA e diverge: não use.

### 1. Identificar Spot e estilo

Leia `dashboard/data/tipologias.js`. Ache o spot pelo nome no `index`.
- Se o entry ja tiver campo `estilo`: use-o.
- Se nao tiver: pergunte -> "Qual o estilo deste Spot? (1) Clean  (2) Biofilico  (3) Industrial  (4) Bruma"
- Salve como `ESTILO` (ex: `clean`, `biofilico`, `industrial`, `bruma`).

Guarde tambem: `SPOT_NAME`, `SLUG`, `TIPOLOGIAS_DRIVE_URL` (campo `drive_url`).

Pergunte tambem (ou use campo do entry, se existir): **tem Taxa Decor (6%)?** — guarde `TEM_DECOR` (sim/nao).

#### 1b. Endereço/CEP do empreendimento (Nekt) — pro cabeçalho e frete

Via `mcp__seazone-hub__nekt-execute_sql`, busque endereço e CEP por `short_name`:
```sql
SELECT street_name, address_number, address_complement, neighborhood, city, state, postal_code
FROM nekt_operacional_bronze.sup_bd_szi_szi_spot_buildings
WHERE short_name = 'SPOT_NAME'  -- ex: 'Natal Spot'
```
Monte `ENDERECO` ("Rua, nº — Bairro, Cidade - UF") e `CEP` (formate 99999-999). Passa pro xlsx (passo 4). Se não achar, deixe em branco.

### 2. Ler o catálogo de preços (Supabase, ao vivo)

A base de valores agora é o app **seazone-decor-interno** (Supabase). Leia ao vivo:

```bash
py -3 "$SKILL_DIR"/scripts/fetch_catalogo.py > tmp/produtos.json
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

> **Unidades — Revit + imagens são obrigatórios (não opcionais).** A capacidade só diz QUAIS
> TIPOS de item entram; NÃO escolhe o modelo (o catálogo tem várias opções de arara, cadeira,
> etc.). Confirme o MODELO escolhido pelo Revit (blocos/famílias da tipologia) + renders e passe
> em `--overrides` (JSON `{tipologia: {role: {item, valor_unitario, cor_acabamento, referencia}}}`)
> — sobrescreve o default da regra por item. A **capacidade** define CONFIGURAÇÃO e quantidades:
> cama queen SEM cama auxiliar (cap. 2) vs COM cama auxiliar (cap. ≥3) é automático; nº de
> cadeiras por capacidade; sofá-cama em cap. 4/5. Roles do `_ITENS_PLUS`: `gabinete_inferior`,
> `cabeceira`, `arara_roupas`, `cama_queen`, `cadeira_jantar`, `cooktop`, etc.

### 4. Gerar memoriais

```bash
py -3 "$SKILL_DIR"/scripts/montar_orcamento.py \
  --tipologias tmp/tipologias_spot.json \
  --produtos tmp/produtos.json \
  --estilo ESTILO \
  --spot "SPOT_NAME" > tmp/memoriais.json
# --sem-decor SE TEM_DECOR = nao (zera a Taxa Decor)
# --overrides tmp/overrides.json com os modelos confirmados no Revit+imagens por tipologia
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
py -3 "$SKILL_DIR"/scripts/gerar_xlsx.py \
  --memoriais tmp/memoriais.json --spot "SPOT_NAME" --saida tmp/Orcamento_SPOT.xlsx \
  --endereco "ENDERECO" --cep "CEP"
```

### 5. Subir o memorial no Drive (UM Sheet, abas por tipologia)

Destino: pasta **`03 - Memorial descritivo`** do Spot
(`Spot / 02 - Projetos / 05 - Projeto Arquitetonico / 10 - Projeto de Interiores / 03 - Memorial descritivo`),
NAO a `02 - Imagens` (la fica so a tabela de tipologias).

Suba o `.xlsx` como **um unico arquivo**, convertido pra Google Sheet (preserva as abas).
As tools do `mcp__drive-raquel__` NÃO aceitam arquivo local nem base64 (só `s3key`), então use o script
(testado 26/10/2026; chave lida de `COMPOSIO_API_KEY`, arquivo sai no nome da Raquel):
```
py -3 "$SKILL_DIR/scripts/subir_xlsx.py" --arquivo "Memorial Descritivo - SPOT_NAME (ESTILO Plus).xlsx" \
   --pasta <id da pasta 03 - Memorial descritivo> --sheets
```
Ele sobe o `.xlsx` (≤5 MB) e cria a cópia em Google Sheet, imprimindo `{"xlsx_id","sheet_id","sheet_url"}`.
Nomeie o `.xlsx` com o nome final antes de subir (o Sheet herda o nome sem a extensão).
Confira depois com `mcp__drive-raquel__GOOGLEDRIVE_FIND_FILE` (`q: "'<id da pasta>' in parents and trashed=false"`).
O Drive converte o `.xlsx` em Google Sheet com **uma aba por tipologia** (+ Resumo). Guarde o link.

> Conta do conector: `mcp__drive-raquel__` autentica como `raquel.tavares` (o arquivo sai no nome dela).
> Nao apague nada pelo MCP; arquivo errado vai pra lixeira do Drive a mao.

### 6. Atualizar a vitrine do dashboard (orcamentos.js)

Agora o memorial e UM unico Sheet (aba Resumo + uma aba por tipologia). Entao:
- `consolidado_url` = link do Sheet do passo 5 (a aba Resumo ja e o consolidado).
- `memorial_url` de cada tipologia = o MESMO link (todas as tipologias estao nesse Sheet, em abas).

Monte `tmp/memorial_urls.json` com todas as tipologias apontando pro mesmo link e rode o script (faz upsert do Spot em `dashboard/data/orcamentos.js`, sem tocar `tipologias.js`):

```bash
# tmp/memorial_urls.json -> {"A": "<link do Sheet>", "B": "<mesmo link>", ...}
py -3 "$SKILL_DIR"/scripts/gerar_dashboard_js.py \
  --orcamentos-js dashboard/data/orcamentos.js \
  --spot "SPOT_NAME" --codigo CODIGO --slug SLUG \
  --estilo ESTILO_CAPITALIZADO \
  --consolidado-url "<link do Sheet do passo 5>" \
  --memoriais tmp/memoriais.json \
  --memorial-urls tmp/memorial_urls.json \
  --gerado-em AAAA-MM-DD
```

Faca commit em BRANCH (nunca direto na `main`) e abra PR pra `staging`/`dev`:
```bash
cd C:/Users/Seazone/Claude/seazone/hackathon-investimentos
git checkout -b feat/orcamento-<slug>
git add dashboard/data/orcamentos.js
git commit -m "feat(orcamento): vitrine do SPOT_NAME no dashboard"   # + linha Co-Authored-By
git push -u origin feat/orcamento-<slug>
gh pr create --base staging   # (ou dev) — nunca --base main sem pedido literal da Raquel
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

## Fluxo ÁREA COMUM (Revit + renders)

Quando o pedido é a área comum (Recepção/Rooftop/Sinalização/Serviços), os ITENS e
QUANTIDADES vêm do **Revit aberto** (MCP) e a COR/ACABAMENTO dos **renders** da pasta
do Spot. Exige Revit aberto + MCP **Revit-SZI** ativo (`mcp__Revit-SZI__get_revit_status`) + link dos renders.
Se as tools não aparecerem, carregue com ToolSearch `"+Revit-SZI"`.

### A1. Coletar blocos do Revit (por ambiente)
- `mcp__Revit-SZI__get_current_view_info` → confirma o modelo/vista (`mcp__Revit-SZI__list_revit_views` lista as vistas).
- Para cada ambiente: `mcp__Revit-SZI__set_active_view(view_name)` e depois
  `mcp__Revit-SZI__ai_element_filter(category=<OST_...>, visible_in_view=true, max_elements=500)`
  em cada categoria de mobiliário: `OST_Furniture`, `OST_Casework`, `OST_LightingFixtures`,
  `OST_PlumbingFixtures`, `OST_Planting`, `OST_SpecialityEquipment` (o parâmetro é o nome do
  BuiltInCategory, não o id numérico). Cada elemento volta com `id`, `category`, `type` (nome do tipo)
  e `level` → agrupe por `type` e conte = blocos. Alternativa: `mcp__Revit-SZI__get_current_view_elements`
  (tudo da vista, agrupado por categoria) e filtre as categorias acima. **Marque a categoria do Revit em
  cada bloco** (`categoria_revit`): é ela que define a categoria do orçamento — generaliza
  pra qualquer projeto (os nomes dos blocos mudam a cada Spot; a categoria não).
  `{"ambiente":"...", "blocos":[{"type_name":"...","qtd":N,"categoria_revit":"OST_Furniture"}]}`
  (o script aceita `OST_Furniture` ou `Furniture`).
- Quando o `type_name` for só a cor (`Cinza`, `Marfim`…), puxe a FAMÍLIA com
  `mcp__Revit-SZI__get_element_properties(element_id=<id de 1 elemento do tipo>, include_type_params=true)`
  (devolve categoria, família, tipo e parâmetros de instância + tipo) e inclua `"family"` — vira o nome do item.

### A2. Revit → linhas
```bash
py -3 "$SKILL_DIR"/scripts/revit_para_linhas.py \
  --blocos tmp/blocos_<amb>.json --produtos tmp/produtos.json --ambiente "<amb>" > tmp/linhas_<amb>.json
```
**Lógica project-agnostic:** categoria vem da `categoria_revit`; item = nome do próprio bloco
(limpo); preço = catálogo quando casar (senão 0). `references/depara-revit.json` é só uma
camada OPCIONAL de apelidos/preço (NÃO o mapa principal — não chumbe blocos de um Spot lá).
Saída: `linhas`, `nao_mapeados` (sem categoria reconhecida → revisar) e `a_precificar`
(itens com valor 0, pra você precificar/confirmar no catálogo).

### A2b. Preço dos itens FORA do catálogo (regras Rosa Sul)
- **Marcenaria:** PRIMEIRO procure a peça no catálogo (usa o preço do catálogo, como qualquer
  item). **Só** se a peça NÃO estiver no catálogo, precifique por área(m²) × R$ 2.000/m² —
  no payload use `{"marcenaria_m2": 9.76}` (área das medidas dos Rooms do Revit —
  `mcp__Revit-SZI__export_room_data`: number/name/level/area_sqm/perimeter_mm; níveis em `mcp__Revit-SZI__list_levels`). Ex. Rosa Sul: balcão/prateleiras = catálogo;
  painel e fechamento mini market = R$ 2.000/m².
- **Pintura** → valor do CATÁLOGO (serviço normal), NÃO taxa por m².
- **Loja** (sofá, quadros, capacho, mesas externas) → preço pesquisado + fornecedor + link.
  **Plantas/vasos = ARTIFICIAIS do Mercado Livre.** **Marmoraria** = orçamento externo (à vista −6%).
- Item do catálogo caro demais → substituir por equivalente do catálogo e anotar.
- Marcenaria/vasos/plantas/tapetes NÃO são modelados no Revit → vêm dos renders + manual.

### A3. Cor/acabamento dos renders
Baixe os renders (`mcp__drive-raquel__GOOGLEDRIVE_FIND_FILE` com `q: "'<id da pasta>' in parents"` →
`mcp__drive-raquel__GOOGLEDRIVE_DOWNLOAD_FILE(fileId)` → devolve URL temporária → `curl -s -o <scratchpad>/render.png "<url>"` →
`Read`) e preencha `cor_acabamento` de cada linha (a cor do render VENCE a do Revit).

### A4. Montar área comum + xlsx
Monte `tmp/area_comum.json` = `{spot, tem_decor, budget, total_unidades, total_pavimentos,
ambientes:[{nome,linhas}], sinalizacao:[{ambiente,qtd}], servicos:[...], sinalizacao_extras:[...]}`.
**Sinalização (auto):** "Nome Spot (logo iluminado)" R$2.500/ambiente + **Números de porta**
(1/unidade × R$150, `total_unidades` do Nekt `total_units`) + **Quadros do marketing**
(4/pavimento × R$150, `total_pavimentos`). Piso tátil/segurança = `sinalizacao_extras` (variam).
**total_unidades** vem do Nekt (`sup_bd_szi_szi_spot_buildings_details.total_units`, join por
`spot_building_id`); **total_pavimentos** do Revit (Levels) ou das tipologias (`total_floors`
do Nekt costuma estar vazio). **Budget**: valor que a Raquel informa por Spot (varia).
```bash
py -3 "$SKILL_DIR"/scripts/montar_area_comum.py --payload tmp/area_comum.json \
  --budget 150000 --saida tmp/Orcamento_SPOT_AreaComum.xlsx \
  --endereco "ENDERECO" --cep "CEP"
```
Gera abas Recepção/Rooftop/Sinalização/Serviços + **Resumo Área Comum**
(SUBTOTAL + Taxa Adm 13% + Taxa Decor 6% + Budget alvo + Saldo). Suba como no passo 5.

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
