# rules.md --- hackathon-investimentos

Preferencias especificas deste projeto (alem das do workspace e do global).

---

## Tabela de tipologias (saida)
- Listar **todas** as unidades, uma a uma, sem abreviar em faixas (ex.: 101, 102, 103... e nao "101-107").
- Ordem das colunas: TIPOLOGIA › N DAS UNIDADES › TERRACO › TIPO › QUANTIDADE › CAPACIDADE › AREAS.
- Totais (tipologias + unidades) numa **unica linha** no rodape.
- Capacidade sempre rotulada como **previsao**, com aviso de confirmar no layout final.

## Orcamento de decor (saida)
- **Sheets SEPARADOS** (um por tipologia + Resumo) — via `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT`. Multi-aba via xlsx NAO funciona na pratica.
- Vai na pasta **`03 - Memorial descritivo`** (dentro de `10 - Projeto de Interiores`), nao na `02 - Imagens`.
- Pacote sempre **Plus**. Custo e **estimativa** (preco de referencia Plus 2026 ou catalogo db002) — a Raquel revisa e ajusta na pre-tabela.
- Itens condicionais (jacuzzi em Garden, etc.) NAO sao universais: conferir a nota da tipologia (ex.: Bonito so a 113 tem jacuzzi) e tratar como excecao.

## Logica de dominio (Spot)
- Capacidade vem da area INTERNA; sacada/varanda nao contam. Seguir a Matriz.
- **Tipo PADRAO e o default**; so marcar PCD quando confirmado na tabela final da Raquel (nao inferir de rotulo "W.C PCD" sozinho).
- **Matriz calibrada (2026-05-27):** <=17 cap2 · ~18 cap3 · ~19-21 cap4 · **>=~22 cap5** · **PCD = -1 nivel** (PCD ~20m2 = cap3).
- **Terraco pelo PAVIMENTO, nao pelo m²:** terreo = Garden (qualquer tamanho, nunca Sacada) · intermediario = Sacada/Varanda · rooftop = Terraco (so se a unidade tiver terraco privativo).
- **PLANTA vence AREA.** O helper agrupa por area+tolerancia e FUNDE demais: default depois de rodar e SEPARAR conferindo a planta. Sinal de layout visto no render (footprint/banheiro/orientacao/esquina) NAO se descarta por resolucao. Criterio de agrupamento e SO layout (confirmado pela Raquel) — nao inventar fatores extras (vista/sol).
- Letras das tipologias (A, B, C...) sao rotulos por ordem; nao precisam casar com a nomenclatura de um PDF antigo.

## Validacao antes de entregar
- Soma das quantidades TEM que fechar com o total de unidades; se nao fechar, avisar, nao entregar como certo.
- Conferir contra verdade conhecida quando houver (Natal = 5 tip / 96 un · Bonito = 6 tip / 53 un · Novo Campeche II = 12 tip / 49 un).

## Acoes no Drive (composio)
- So CRIAR planilha nova; nunca sobrescrever arquivo existente.
- Confirmar owner do conector antes de criar em pasta do time.
- **Conta do conector**: conectado como `raquel.tavares@seazone.com.br` (2026-05-27 noite). Drive e Sheets sao OAuth separados — autorizar ambos quando solicitado.
- **Sem delete**: este MCP Composio NAO apaga arquivos. Se criar no lugar errado, avisar a Raquel pra mandar pra lixeira.
- **Upload**: criar Sheets via `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` (CSV->Sheet). Popular via `GOOGLESHEETS_UPDATE_VALUES_BATCH`. Xlsx multi-aba NAO funciona na pratica (Drive converte em 1 aba; base64 nao chega no sandbox) — usar Sheets SEPARADOS.
