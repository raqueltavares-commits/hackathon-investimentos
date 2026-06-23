# Plano — Validação via Revit na skill `tabela-tipologias`

## Objetivo
Adicionar à `tabela-tipologias` um passo **opcional** que lê o **Revit aberto** (MCP Nonica)
para **validar e enriquecer** a tabela de tipologias. O Revit é COMPLEMENTO — a fonte da
tabela continua sendo o **anteprojeto LANÇAMENTOS** (regra do projeto). Divergência Revit ×
anteprojeto é INFORMAÇÃO pra revisão, nunca correção automática.

## O que o Revit valida
1. **Áreas / capacidade** — Rooms (OST_Rooms -2000160): área interna por unidade → confere a
   capacidade deduzida da área do anteprojeto. Δ acima da tolerância vira alerta.
2. **Contagem de unidades por pavimento** — nº de Rooms de unidade por nível × o total do
   anteprojeto (refs: Natal 96, Bonito 53, Novo Campeche II 49).
3. **Esquadrias por tipologia** — janelas (OST_Windows -2000014) e portas (OST_Doors -2000023)
   por unidade: as unidades de um mesmo grupo têm o mesmo nº/تtipo? Se uma diverge → sinal de
   tipologia separada (igual à lógica de esquina do DWG, mas via Revit). Segunda opinião ao A-GLAZ.
4. **Terraço/sacada e pé-direito** — confirma o campo Terraço.

## Onde encaixa no procedimento atual
- Novo passo **2c — Validação Revit (opcional)**, depois do levantamento DWG/PDF (passo 2),
  alimentando o agrupamento (passo 4) com uma segunda opinião.
- Saída ganha **aba/coluna "Revit confere?"** + lista de divergências no resumo executivo.
- `fontes` (dashboard) ganha **`revit: true/false`** (nova tag verde/vermelho na vitrine).
- O agrupamento final continua mandado pelo **layout/anteprojeto** (regra da Raquel).

## Coleta (agente, via MCP) → JSON project-agnostic
`get_active_view_in_revit` (confirma modelo) → por nível de unidades:
- Rooms: `get_elements_by_category(-2000160, viewId)` → `get_parameters_from_elementid`
  (Number/Name + Área + Level).
- Janelas/portas: `get_elements_by_category(-2000014 / -2000023, viewId)`; associar à unidade
  pela Room (porta tem from/to room; janela pelo host wall que limita a Room — NEAREST-ROOM,
  igual ao NEAREST-LABEL do DWG).
Monta:
```json
{"unidades": [{"unidade":"101","nivel":1,"area_revit":16.84,"janelas":2,"portas":1}]}
```

## Novo script — `scripts/validar_revit.py` (puro, testável)
Entrada: `unidades.json` (classificação atual) + `revit.json` (acima). Casa por número de
unidade (normalizado). Saída:
```json
{"validacoes":[{"unidade":"101","area_ok":true,"delta_area":0.0,
                "capacidade_ok":true,"janelas":2}],
 "esquadrias_por_tipologia":{"A":{"janelas":[2],"consistente":true}},
 "divergencias":["108: área Revit 23,4 vs anteprojeto 18,2 → revisar capacidade"],
 "ok":true}
```
Regras:
- `area_ok` = |area_revit − area_util| ≤ TOL (default **0,5 m²**, configurável).
- `capacidade_ok` = capacidade da Matriz pela area_revit == capacidade da classificação.
- `esquadrias_por_tipologia.consistente` = todas as unidades do grupo têm o mesmo nº de janelas.
- Sem `revit.json` → passo é pulado, tabela sai como hoje (Revit é opcional).

## Faseamento (TDD)
- **Fase 1 (sólida) — FEITO:** validação por **Rooms** (área + contagem + capacidade).
  Casamento por número de unidade. `validar_revit.py`.
- **Fase 2 (heurística) — FEITO:** **esquadrias por grupo** (nº de janelas por unidade;
  divergência dentro do grupo terraço+tipo+capacidade+área → possível tipologia separada).
  Pendente apenas validar a ASSOCIAÇÃO esquadria→unidade (NEAREST-ROOM) no modelo real
  antes de confiar 100% — a lógica de consistência já está testada.

## Decisões a confirmar com a Raquel
1. **Tolerância de área** pra alerta: 0,5 m²? (fronteiras da Matriz de capacidade são sensíveis).
2. Quando Revit diverge do anteprojeto, a tabela sai pelo **anteprojeto** (Revit só sinaliza) — confirmar.
3. Esquadria: usar janela (OST_Windows) como sinal principal, porta como apoio? (igual DWG).

## Riscos
- Revit pode ser versão/etapa diferente do anteprojeto LANÇAMENTOS → por isso valida, não corrige.
- Associação esquadria→unidade é heurística; pode falhar em layout aberto (porta em vez de janela).
- Exige Revit aberto + Nonica; sem isso, nada muda.
