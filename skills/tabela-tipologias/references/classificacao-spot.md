# Classificação de tipologias Spot

Cada unidade é classificada por **Terraço + Tipo construtivo + Capacidade**.

## Terraço / Área externa
Sem · Sacada · Varanda · Garden · Terraço.

**Quem decide o rótulo é o PAVIMENTO, não o tamanho em m²:**
- **Térreo** → área externa privativa é **Garden** (é chão/quintal), por menor que seja
  (mesmo ~5 m²). NUNCA "Sacada" no térreo. (Erro real Novo Campeche II: classifiquei
  101-110 como Sacada pela área de ~5 m² — eram todas Garden.)
- **Pisos intermediários** → varanda elevada = **Sacada** (compacta) ou **Varanda** (maior).
- **Rooftop/cobertura** → **Terraço** (quando a unidade tem terraço privativo). Mas
  "rooftop = terraço" NÃO é universal: se a cobertura for área comum (piscina/lazer), a
  unidade do último piso pode ser "Sem sacada". A planta decide.
- Pavimento tipo sem área externa = **Sem** (ou "Sem sacada").

## Tipo construtivo
Padrão · PCD (porta de correr, raio de giro Ø 1,50m, acesso bilateral à cama) ·
Mezanino (2 pisos) · Único.

## Capacidade (PREVISÃO — confirmar com layout final)
**Regra de ouro:** a capacidade é deduzida **SEMPRE pela área INTERNA** da unidade
(privativa coberta), aplicando a Matriz. **NUNCA** conte a área de sacada / varanda /
terraço para a capacidade — área externa não vira leito. E **não confie** na coluna
CAPACIDADE do `ANÁLISE.xlsx` (já veio errada): use o ANÁLISE só para as áreas.

Derivada da área interna + programa de mobiliário:
- **Base (cap. 2):** Cama Queen + cabeceira + copa linear + bancada + arara +
  vassoureiro + TV. 60cm de circulação ao redor da cama; 20cm cama↔janela.
- **Cama auxiliar** (0,67×1,90m) cabe ao lado da Queen → habilita **cap. 3 e 5**.
- **Sofá-cama** (aberto 1,62×2,00m = leito) → habilita **cap. 4 e 5**.
- Duas unidades com a **mesma área interna** têm a **mesma capacidade**, mesmo que
  uma tenha sacada e a outra não (ex.: Natal 408 com sacada = cap 3, igual às
  internas de 18 m²; a sacada não soma capacidade).

Matriz resumida:
| Capacidade | Cama auxiliar | Sofá-cama |
|-----------|---------------|-----------|
| 2         | não           | não       |
| 3         | sim           | não       |
| 4         | não           | sim       |
| 5         | sim           | sim       |

Guia de previsão por metragem interna (sempre PREVISÃO, confirmar no layout):
- até ~17 m² → **cap 2** (só a base).
- ~18 m² → **cap 3** (cabe cama auxiliar).
- ~19–21 m² → **cap 4** (cabe sofá-cama).
- **≥ ~22 m² → cap 5** (cabe cama auxiliar + sofá-cama). (Calibrado em Novo Campeche II:
  22,1 m² interno já é cap 5 — o limiar antigo "~23" era alto demais.)

**PCD rende um nível ABAIXO do que a área crua sugere.** O giro Ø1,50m + acesso bilateral
à cama comem área útil, então não aplique a matriz direto. Ex. Novo Campeche II: unidades
PCD de ~20 m² (101, 106) = **cap 3**, não cap 4. Regra prática: PCD ≈ (cap da área) − 1.

## Agrupamento em tipologias — REGRA (decide pela PLANTA, não pela área)
O que define a tipologia é o **DESENHO**: mesma posição de banheiro e o **mesmo
número/tipo de esquadrias (janelas)**. A metragem é só pista — não decide.
- **Espelhamento** (unidade idêntica, só espelhada) = **MESMA** tipologia.
- Desenho e esquadrias iguais, **só muda um pouco o m²** = **MESMA** tipologia.
- Tem **uma esquadria a mais** (ex.: janela de esquina) = **OUTRA** tipologia,
  mesmo que à primeira vista pareça igual. (Geralmente a de esquina é um pouco maior.)

Por isso o agrupamento por área do helper é só ponto de partida: **conferir na planta**
quantas esquadrias cada unidade tem. Terraço + Tipo + Capacidade continuam separando também.

**REGRA-MÃE (quando planta e área discordam, a PLANTA vence).** O helper agrupa por
(terraço+tipo+cap) com tolerância de área (~1 m²) e por isso **FUNDE demais**: unidades de
área quase igual mas layout diferente caem juntas. O default DEPOIS de rodar o helper é
**SEPARAR conferindo a planta**, não aceitar a fusão. Sinal de layout visto no render
(footprint diferente, orientação da cama, posição do banheiro, esquina) **NÃO se descarta
por causa da resolução** — se dá pra ver diferença, é tipologia candidata a separar.
(Erro real Novo Campeche II: fundi 28 unidades do pav tipo numa só; eram TRÊS — coluna
direita 207-209/307-309, núcleo 216/316, e o miolo. Eu tinha VISTO a diferença no render
e descartei. O rooftop, idem: 4 layouts, não 2.)
