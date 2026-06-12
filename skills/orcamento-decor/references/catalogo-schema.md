# Fonte do catálogo de preços

A base de valores migrou do Sheet do Drive (`db002_produtos`) para o app interno
**seazone-decor-interno** (Supabase `cjbsotszriddpadznhvk`, tabela `produto`).

## Como a skill lê
`scripts/fetch_catalogo.py`:
1. GET `https://seazone-decor-interno.seazone.properties/` → acha `assets/index-*.js`.
2. GET do bundle → extrai a anon key (JWT) embutida.
3. GET `…/rest/v1/produto?select=codigo,nome,valor,subcategoria_codigo&codigo=in.(...)`
   com header `apikey` (RLS libera leitura anon).
4. Mapeia `produto.codigo` → código-item via `depara-catalogo.json` e devolve
   `{codigo-item: {nome, categoria, valor_unitario, unidade}}`.

## De-para (`depara-catalogo.json`)
Liga cada um dos 33 itens-template da skill a UM `produto.codigo` exato da base,
escolhido pelo produto mais usado nos memoriais Plus reais (`produto_tipologia`).
Regra de valor: SEMPRE seguir o que a base usa (fonte mais atualizada); sem override manual.

## Encoding
Campos texto vêm com double-encoding (UTF-8 lido como latin1). `normalizar()` corrige.

## Fallback
`ler_catalogo.py` (parse de CSV) permanece como fallback offline.
