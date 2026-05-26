# rules.md --- hackathon-investimentos

Preferencias especificas deste projeto (alem das do workspace e do global).

---

## Tabela de tipologias (saida)
- Listar **todas** as unidades, uma a uma, sem abreviar em faixas (ex.: 101, 102, 103... e nao "101-107").
- Ordem das colunas: TIPOLOGIA › N DAS UNIDADES › TERRACO › TIPO › QUANTIDADE › CAPACIDADE › AREAS.
- Totais (tipologias + unidades) numa **unica linha** no rodape.
- Capacidade sempre rotulada como **previsao**, com aviso de confirmar no layout final.

## Logica de dominio (Spot)
- Capacidade vem da area INTERNA; sacada/varanda nao contam. Seguir a Matriz.
- Letras das tipologias (A, B, C...) sao rotulos por ordem (quantidade desc); nao precisam casar com a nomenclatura de um PDF antigo.

## Validacao antes de entregar
- Soma das quantidades TEM que fechar com o total de unidades; se nao fechar, avisar, nao entregar como certo.
- Conferir contra verdade conhecida quando houver (Natal = 5 tipologias / 96 unidades).

## Acoes no Drive (compartilhado)
- So CRIAR planilha nova; nunca sobrescrever arquivo existente.
- Confirmar com a Raquel antes de escrever em pasta do time.
