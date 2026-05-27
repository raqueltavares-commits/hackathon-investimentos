# Schema do db002_produtos

> **Preencher na primeira execucao real.** Inspecione as colunas do CSV
> antes de rodar `ler_catalogo.py` em producao.

## ID do Sheet
`1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o` — aba db002_produtos (gid: 1263042396)

## Como inspecionar
Baixe via Drive (exportMimeType: text/csv) e rode:
```
python ler_catalogo.py --csv db002.csv 2>&1
```
Se falhar, o erro lista as colunas disponíveis. Se passar, documente aqui.

## Colunas esperadas (a confirmar)
- `codigo` (ou variante) — codigo do produto (ex: MRC0002, MOB0001)
- `nome` (ou variante) — descricao do item
- `categoria` (ou variante) — MARCENARIA | MOBILIARIO | ELETROS | etc.
- `valor_unitario` (ou variante) — preco em reais (ex: 3300.00 ou "R$ 3.300,00")
- `unidade` (opcional) — un, m2, kit

## Mapeamento manual (se auto-deteccao falhar)
```
python ler_catalogo.py --csv db002.csv \
  --col-codigo <nome_real_da_coluna> \
  --col-nome <nome_real_da_coluna> \
  --col-categoria <nome_real_da_coluna> \
  --col-valor_unitario <nome_real_da_coluna>
```
