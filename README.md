# Padrão Spot — Tipologias & Decor (Hackathon SZI · Trilha Decor)

Ferramentas de IA para o time de **Lançamentos / Interiores** da Seazone montar, a partir do
anteprojeto dos empreendimentos **Spot**, a **tabela de tipologias** de cada empreendimento —
o passo que hoje depende do conhecimento na cabeça de quem faz.

> Autora: Raquel Tavares (Especialista em Interiores · Lançamentos · Seazone Investimentos)
> Construído com **Claude Code**, usando dados reais da SZI.

---

## O problema
Antes de mobiliar um Spot, é preciso classificar cada unidade do anteprojeto em **tipologias**
(grupos que recebem o mesmo pacote de decoração). Isso exige cruzar PDF + planilha + plantas e
aplicar regras de capacidade/terraço/layout que não estavam documentadas em lugar nenhum.

## A solução
1. **Skill `tabela-tipologias`** (Claude Code) — puxa o anteprojeto **LANÇAMENTOS** do Drive,
   lê PDF + comparativo de áreas + **DWG** (esquadrias por pavimento, via ODA + ezdxf),
   classifica cada unidade (terraço · tipo · capacidade-previsão pela área interna) e agrupa
   em tipologias, gerando um **Google Sheet editável** na pasta de Interiores do próprio Spot.
2. **Dashboard "Padrão Spot"** (`dashboard/`) — site estático que documenta a lógica das
   tipologias e o programa de mobiliário, + uma vitrine das tabelas geradas por Spot, com
   selos de quais fontes alimentaram cada tabela (PDF / Análise / DWG).

## Como usar (no Claude Code)
```
monta a tabela de tipologias do <NOME DO SPOT>
```
O Claude segue o `SKILL.md`: acha o anteprojeto LANÇAMENTOS no Drive (nunca "COMPATIBILIZADO
INTERIORES"), lê PDF + DWG, classifica, agrupa, **valida o total** e cria o Sheet — devolvendo
o link. O agrupamento por layout é confirmado na planta (a área é só ponto de partida).

## Regras de domínio que a skill aplica
- **Capacidade** deduzida SEMPRE pela **área interna** (privativa coberta), via Matriz —
  nunca pela sacada/terraço, nunca pela coluna do ANÁLISE. É **previsão** até o layout final.
  Calibração: ≤17→cap2 · ~18→cap3 · ~19-21→cap4 · ≥~22→cap5 · **PCD = −1 nível**.
- **Terraço pelo pavimento**: térreo → Garden · intermediário → Sacada/Varanda · rooftop → Terraço.
- **Planta vence área**: unidades de área parecida mas layout diferente são tipologias distintas.

## Validação de referência
- **Natal Spot** → 5 tipologias / 96 unidades
- **Novo Campeche Spot II** → 12 tipologias / 49 unidades

## Estrutura
```
skills/tabela-tipologias/   a skill (SKILL.md, scripts/, references/)
dashboard/                  o site "Padrão Spot" (HTML/CSS/JS estático)
tests/                      testes pytest do helper + leitura DWG
docs/                       CSVs versionados das tabelas geradas + specs
CLAUDE.md memory.md lessons.md rules.md   arquivos de contexto do projeto
```

## Rodar localmente
```bash
python -m pytest tests/ -q                 # testes
python -m http.server 5500 --directory dashboard   # dashboard em http://localhost:5500
```
Dependências: Python 3.12 (`pytest`, `ezdxf`, `pymupdf`, `openpyxl`, `pillow`) +
**ODA File Converter** (para ler DWG).

## Arquivos de contexto (avaliação)
`CLAUDE.md` (manual do projeto) · `memory.md` (decisões e estado) · `lessons.md` (erros a não
repetir, com o caso real do Novo Campeche II) · `rules.md` (convenções de saída e domínio).
