# Memorial final: Revit + renders + catálogo vivo — Design

**Data:** 2026-06-12
**Escopo:** somente a skill `orcamento-decor`. NÃO altera `tabela-tipologias` nem outras skills.

## Objetivo

Evoluir a `orcamento-decor` de uma heurística que **inventa** a lista de itens (33 itens fixos por capacidade) para um motor que gera o memorial a partir do **projeto real**: lê o modelo Revit aberto, avalia os renders finais, casa item por item com o catálogo da Decor (agora no Supabase) e gera o memorial precificado.

## Dois tipos de memorial (decide a segmentação)

| Tipo | Eixo de corte | Tipologia? | Exemplo |
|---|---|---|---|
| **Unidade** | TIPOLOGIA (A, B, D...) | sim | Bonito, Natal, Novo Campeche |
| **Área comum** | AMBIENTE — sempre 3 seções fixas: **Recepção, Corredor, Rooftop** | não | Rosa Sul (Rooftop = "Ático" neste arquivo) |

O tipo é a primeira decisão do fluxo e ramifica só o **eixo de agrupamento** — catálogo, matching e formato de saída são compartilhados.

## Fontes de dados

- **Catálogo (preço/produto):** Supabase `cjbsotszriddpadznhvk`, tabela `produto`, via PostgREST + anon key extraída do bundle de produção em runtime (RLS libera leitura anon). Aposenta o CSV do Drive (`db002_produtos`).
- **BOM (itens reais):** Revit aberto via MCP (validado funcionando em 2026-06-12). Categorias de decor: Mobiliário (Furniture), Marcenaria (Casework), Louças e Metais (Plumbing), Eletros (Specialty/Electrical), Iluminação (Lighting). Segmentação por OST_Rooms nomeados.
- **Renders:** Google Drive, pasta `02 - Imagens` do Spot.

## Arquitetura em fases (cada fase entrega valor sozinha)

### Fase A — Catálogo vivo  *(fundação; ~90% pronta)*
Substitui "baixar CSV do Drive + parsear" por "ler `valor` da base Supabase". Mantém o resto da skill intacto.
- Novo leitor: `ler_catalogo.py` reescrito (ou `fetch_catalogo.py`) → busca anon key no bundle, consulta `produto`, normaliza encoding double-UTF8, devolve preços.
- **De-para item→produto exato** (33 itens → `produto.codigo`), data-driven (produto mais usado nos memoriais Plus reais em `produto_tipologia`). Salvo como artefato versionado na skill.
- `montar_orcamento.py` consome igual a hoje (lookup por código do item). Mudança isolada no leitor.
- **Regra de valor (decidida):** SEMPRE usar o que a nova base utiliza — ela é a versão mais atualizada. O de-para fica data-driven pelo produto mais usado nos memoriais Plus reais; sem override manual de preço.

### Fase B — BOM do Revit
Lê o modelo aberto e extrai a lista real de itens por seção.
- **Área comum:** filtra elementos das categorias de decor por Room ∈ {Recepção, Corredor, Rooftop/Ático}. Cada room vira uma seção do memorial.
- **Unidade:** segmenta por tipologia (Room/parâmetro de tipologia). Reusa o mesmo motor, troca o eixo.
- Por item: família/tipo, quantidade, ambiente, dimensões (parâmetros).
- Saída: BOM estruturado por seção → entra no lugar da lista fixa de `montar_orcamento.py`.

### Fase C — Casamento com o catálogo
Cada item do BOM → produto do catálogo (código + preço).
- Matching por nome + dimensão + categoria/subcategoria; pontua confiança.
- Reusa a lógica do de-para da Fase A como dicionário-semente.
- Itens de baixa confiança entram numa **etapa de revisão** (a Raquel confirma o produto, como na validação do de-para). Sem match → fallback configurável.

### Fase D — Renders (visão)
Avalia as imagens finais da pasta `02 - Imagens`.
- Confirma estilo/acabamento (Clean/Biofílico/Industrial/Bruma) por seção.
- Captura itens decorativos ausentes do Revit (almofadas, objetos, enxoval, tapetes).
- Camada de complemento/validação sobre o BOM — não substitui o Revit.

### Fase E — Memorial final
Consolida BOM + preços + acabamentos → xlsx multi-aba (uma aba por tipologia OU por ambiente) + Resumo, sobe no Drive e alimenta o dashboard. **Reusa `gerar_xlsx.py` / `gerar_dashboard_js.py` atuais** (troca o eixo de aba quando for área comum).

## Sequência recomendada
1. Fechar **Fase A** (fundação compartilhada, valor imediato).
2. **Fase B na ramificação área comum** (Rosa Sul está aberto e é o caso real em mãos).
3. **Fase C** (matching) → **Fase D** (renders).
4. Ramificação **unidade/tipologia** em paralelo, reusando o motor.

## Riscos
- **Matching Revit↔catálogo:** nomes de família não batem com nomes do catálogo → exige etapa de revisão humana (mitigado pela Fase C).
- **Estrutura do Revit varia por projeto:** rooms podem não estar nomeados como esperado → validar por projeto, configurável.
- **Anon key rotaciona:** mitigado lendo do bundle em runtime.
- **Encoding double-UTF8** no Supabase → normalizar na leitura.
- Memorial é **estimativa** — a Raquel revisa.

## Não-objetivos
- Não escrever no Supabase nem no Revit (somente leitura).
- Não mexer em `tabela-tipologias` nem no app `seazone-decor-interno`.
- Não ler `produto_tipologia` como fonte do memorial (a lista vem do Revit; `produto_tipologia` serve só pra calibrar o de-para).
