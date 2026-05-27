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
- **Matriz calibrada (2026-05-27):** <=17 cap2 · ~18 cap3 · ~19-21 cap4 · **>=~22 cap5** · **PCD = -1 nivel** (PCD ~20m2 = cap3).
- **Terraco pelo PAVIMENTO, nao pelo m²:** terreo = Garden (qualquer tamanho, nunca Sacada) · intermediario = Sacada/Varanda · rooftop = Terraco (so se a unidade tiver terraco privativo).
- **PLANTA vence AREA.** O helper agrupa por area+tolerancia e FUNDE demais: default depois de rodar e SEPARAR conferindo a planta. Sinal de layout visto no render (footprint/banheiro/orientacao/esquina) NAO se descarta por resolucao. Criterio de agrupamento e SO layout (confirmado pela Raquel) — nao inventar fatores extras (vista/sol).
- Letras das tipologias (A, B, C...) sao rotulos por ordem; nao precisam casar com a nomenclatura de um PDF antigo.

## Validacao antes de entregar
- Soma das quantidades TEM que fechar com o total de unidades; se nao fechar, avisar, nao entregar como certo.
- Conferir contra verdade conhecida quando houver (Natal = 5 tip / 96 un · Novo Campeche II = 12 tip / 49 un).

## Acoes no Drive (compartilhado)
- So CRIAR planilha nova; nunca sobrescrever arquivo existente.
- Confirmar com a Raquel antes de escrever em pasta do time.
