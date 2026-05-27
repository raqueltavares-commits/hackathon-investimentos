# Plano — hackathon-investimentos — atualizado 2026-05-27

## Onde paramos
- **Skill `tabela-tipologias`**: helper Python testado, gera CSV + Google Sheet no Drive + alimenta a vitrine. OK.
- **Dashboard "Padrão Spot"**: 2 abas. "Tipologias por Spot" agora mostra a fonte
  por spot (tags PDF/Análise/DWG, verde tem / vermelho não tem) e o bloco
  "De onde vem a precisão" com as 3 fontes. Validado no preview. Commit `e519cb9`.
- **Leitura DWG**: VALIDADA contra o DWG real do Bonito (3 pisos, baixados do Drive).
  Resultado: o `ler_dwg.py` atual **retorna `{}`** no arquivo real (a fixture sintética
  não batia com o export Revit). Método correto descoberto e validado — falta reescrever.

## Tarefa #1 (PRIO 1) — reescrever `ler_dwg.py`
**Abordagem validada** (ver memory.md / lessons.md 2026-05-27):
- Focar na **planta de áreas** (região x dos labels de unidade).
- **nearest-label**: atribuir cada bloco `A-GLAZ` à unidade mais próxima (NÃO reconstruir
  polígono — os boundaries `A-AREA-BNDY` são segmentos LINE soltos, não polilinhas).
- Emitir uma **assinatura por unidade** (contagem de janela) pra AGRUPAR — não uma tabela
  de esquadrias. Agrupar pela contagem crua por piso.
- **Portas saem da assinatura** (área comum contamina o nearest-label).
- **Térreo**: a janela pode faltar (abre por porta de correr) — lá o agrupamento sai da
  ÁREA (PDF) + layout/rótulo (W.C PCD, garden). NUNCA excluir o térreo: pode ter unidades
  diferentes.

**Verdade conhecida (Bonito)**: tipo = 12 padrão + 4 esquina (203,204,212,213);
rooftop = 6 padrão + 2 esquina (403,404) — bate com as J02 do PDF.
DWGs baixados em `tmp/` (gitignored). IDs no Drive em memory.md.

**Critério de pronto**: rodar contra os 3 pisos do Bonito e reproduzir o agrupamento acima.

## Tarefa #2 (PRIO 2) — hospedar o dashboard num link
HTML estático — deploy simples (Coolify ou análogo).

## Tarefa #3 (PRIO 3) — Fase 2: Orçamento do decor
Integrar catálogo de móveis e gerar orçamento preliminar por tipologia.

---

## Links úteis
- Natal Sheet: https://docs.google.com/spreadsheets/d/1Ffn359MFIgtERfKWiR-UfMFJVUOWDotSaSQLm8PxXQ8/edit
- Bonito Sheet (rascunho): https://docs.google.com/spreadsheets/d/1iq7gvHOmMwSrw0HwK8iT6Ssa0MRFyKIeAobpdZ7txNM/edit
- Plano DWG: docs/superpowers/plans/2026-05-27-dwg-tipologias.md
- Leitura DWG (referência): skills/tabela-tipologias/references/dwg-leitura.md
