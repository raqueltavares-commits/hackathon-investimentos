# Aba "Tipologias por Spot" (vitrine) — Design

**Data:** 2026-05-26 · Dashboard Padrao Spot, 2ª aba.

## Objetivo
Vitrine das tabelas de tipologias **já geradas** pelo Claude. Todo o time vê; a geração continua sendo feita pelo Claude (decisão de arquitetura — PDF como fonte, IA no fluxo). Não gera no navegador (isso é a opção 3, futura).

## Dados (sincronia)
Quando a skill gera um Spot, além do Google Sheet ela escreve no dashboard:
- `dashboard/data/tipologias/<slug>.json` — `{ spot, codigo, slug, gerado_em, drive_url, total_tipologias, total_unidades, colunas, tipologias:[{tipologia,unidades:[],terraco,tipo,quantidade,capacidade,area_util,area_unidade}] }`.
- `dashboard/data/tipologias/index.json` — lista `[{ spot, codigo, slug, gerado_em, total_tipologias, total_unidades, drive_url }]`.

Carregados como JS global (`window.TIPOLOGIAS_INDEX`, e cada Spot via `<script>` sob demanda) pra abrir via file:// sem servidor — mesmo padrao do `padrao-spot.js`.

## Tela
1. **Barra de busca** (nome + código) no topo da aba.
2. **Cards** dos Spots gerados (filtram conforme digita): nome, código, data, totais (X tipologias / Y unidades), botões **"Ver tabela"** e **"Abrir no Drive"**.
3. **"Ver tabela"** → expande a tabela completa inline (mesmas colunas/estilo da aba Lógica & Regras; unidades sem abreviar).
4. **Busca sem match** → aviso "ainda não gerado" + botão **"Pedir geração ao Claude"** que copia pro clipboard o comando `gera a tabela de tipologias do <Spot digitado>`.
5. **Estado vazio** (nenhum Spot gerado): mensagem amigável + a busca/pedir-geração.

## Técnico
- Fazer as **abas funcionarem** (hoje só "Lógica & Regras" ativa). Adicionar 2º painel `#panel-tipologias` e navegação em `app.js` (mostra/esconde painel, marca aba ativa). A aba "Orçamento" segue "em breve".
- Reusar estilos/marca existentes; render de tabela compartilhado.
- Atualizar `SKILL.md`: novo passo "escrever os JSONs do dashboard" ao gerar.

## Fora de escopo
Geração no navegador (opção 3). Edição da tabela na vitrine (editável é no Google Sheet).

## Teste
Visual no navegador, com `index.json` populado pelo Natal (que já temos) pra ver a vitrine cheia + o fluxo de busca sem match.
