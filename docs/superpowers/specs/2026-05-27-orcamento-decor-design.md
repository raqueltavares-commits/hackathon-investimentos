# Design — Fase 2: Orçamento Preliminar do Decor

**Data:** 2026-05-27  
**Projeto:** hackathon-investimentos (trilha Decor)  
**Fase:** 2 de 2 (Fase 1 = skill tabela-tipologias, já entregue)

---

## Contexto

A Fase 1 gerou a skill `tabela-tipologias`, que lê o anteprojeto de um Spot novo e produz uma tabela de tipologias (Terraço · Tipo · Capacidade) em um Google Sheet no Drive. O dashboard vitrine mostra os spots gerados.

A Fase 2 fecha o loop: dado o resultado da Fase 1, gera o **memorial descritivo preliminar de decor** por tipologia — com todos os itens, quantidades e preços de referência puxados do catálogo real.

---

## Objetivo

Para qualquer Spot cujas tipologias já foram geradas (Natal, Bonito, Novo Campeche II, ou futuros), produzir:

1. **Sheet de orçamento no Drive do Spot** — uma aba por tipologia, cada aba com o memorial completo (categorias · itens · qtd · valor unitário · total · subtotais por categoria · Taxa Decor · Taxa Adm · Total Geral).
2. **Coluna "Custo estimado decor"** adicionada ao Sheet de tipologias existente — custo total por tipologia em uma linha, fácil de ver junto com a tabela já usada pela Raquel.

## Dimensões do orçamento

| Dimensão | Valor | Como determinar |
|---|---|---|
| **Pacote** | Sempre **Plus** | Fixo — não perguntar |
| **Estilo** | Clean · Biofílico · Industrial · Bruma | Perguntar na invocação (ou já registrado no spot) |
| **Capacidade** | 2 · 3 · 4 · 5 | Vem da tabela de tipologias |
| **Terraço** | Sem · Sacada · Garden · Terraço | Vem da tabela de tipologias |
| **Tipo** | Padrão · PCD | Vem da tabela de tipologias |

O estilo afeta:
- Quais itens de mobiliário solto são usados (cada estilo tem uma paleta de peças diferente)
- O acabamento/material da marcenaria (ex: Industrial = metal grafite; Biofílico = palhinha)
- A referência de preço para cada item

Fontes por estilo:
- **Marcenaria por estilo+pacote**: Sheet `1VnEZ-2UscCx03cwEGEDVA9vbfaUw4Y04wiM_lh9YRYI` (aba por estilo/pacote)
- **Mobiliário solto por estilo**: docs "PADRÃO ESTILO X" no Drive de cada estilo
- **Preços base**: `db002_produtos` no catálogo principal

---

## Arquitetura

```
skills/orcamento-decor/
  SKILL.md
  scripts/
    ler_catalogo.py        # lê db002_produtos do Drive → dict de produtos
    montar_orcamento.py    # tipologias + produtos → memoriais por tipologia
    gerar_sheet.py         # cria Sheet no Drive + atualiza Sheet de tipologias
  references/
    itens-por-capacidade.md   # regra de quais itens entram por cap/terraço/PCD
    catalogo-schema.md        # colunas do db002_produtos (a documentar na 1ª run)

tests/
  test_montar_orcamento.py
  test_ler_catalogo.py
```

---

## Componentes

### `ler_catalogo.py`

- **Entrada:** ID do Google Sheet do catálogo (`1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o`)
- **Como lê:** Download via Drive MCP (`download_file_content` com `exportMimeType=text/csv`) da aba `db002_produtos` (gid=1263042396)
- **Saída:** `dict[str, Produto]` keyed por código do item (ex: `"MRC0002"`)

```python
@dataclass
class Produto:
    codigo: str
    nome: str
    categoria: str        # MARCENARIA | MOBILIÁRIO | ELETROS | METAIS | MARMORARIA | ...
    valor_unitario: float
    unidade: str          # un, m², kit
```

- Schema real do db002 a inspecionar na primeira execução e documentado em `catalogo-schema.md`.

### `montar_orcamento.py`

- **Entrada:** lista de `Tipologia` (do Sheet de tipologias gerado na Fase 1) + `dict[str, Produto]`
- **Lógica de itens por tipologia:**

| Condição | Itens adicionados |
|---|---|
| Sempre (todas as caps) | Copa linear, Gabinete inferior, Gabinete superior, Bancada cozinha (pedra), Bancada banheiro (pedra), Metais cozinha, Metais banheiro, Eletros fixos (cooktop, frigobar, microondas, cafeteira, chaleira, liquidificador, depurador), Iluminação, Box banheiro, TV 43" |
| Cap. 3 ou 5 | Cama auxiliar |
| Cap. 4 ou 5 | Sofá-cama |
| Cap. 2 | Bancada 2 cadeiras; Cap. 3 → 3 cadeiras; Cap. 4 → 3–4; Cap. 5 → 4–5 |
| Terraço = Garden ou Terraço | Jacuzzi circular |
| Terraço = Varanda ou Sacada | Mesa externa + cadeiras |
| Tipo = PCD | Banheiro PCD (spec diferente); Arara PCD |

- **Saída:** lista de `MemorialTipologia`

```python
@dataclass
class LinhaMemorial:
    categoria: str
    item: str
    quantidade: int
    valor_unitario: float
    valor_total: float

@dataclass
class MemorialTipologia:
    tipologia: str        # ex: "A — Sem Sacada · Padrão · Cap. 4"
    linhas: list[LinhaMemorial]
    subtotais: dict[str, float]    # por categoria
    taxa_decor: float     # fixo R$ 2.500
    taxa_adm: float       # 13% do valor_produtos
    total_geral: float
    valor_produtos: float
```

### `gerar_sheet.py`

- **Entrada:** lista de `MemorialTipologia` + ID pasta destino no Drive do Spot + ID Sheet tipologias existente
- **Como cria o Sheet de orçamento:**
  - **Estratégia adotada:** CSV formatado com separador `---SHEET:<nome>---` entre tipologias — mesma técnica da Fase 1 (Drive converte pra Sheet editável com múltiplas abas).
  - Destino: mesma pasta `05 - Projeto Arquitetonico / 10 - Projeto de Interiores / 02 - Imagens` do Spot.
- **Como atualiza o Sheet de tipologias:**
  - Baixa o CSV atual do Sheet de tipologias via Drive.
  - Adiciona coluna `CUSTO ESTIMADO DECOR` com o `total_geral` de cada tipologia.
  - Cria um **novo Sheet** com nome `<nome-original> + Custo` — nunca modifica o Sheet original.

---

## Fluxo da skill (SKILL.md)

```
1. Usuário: "gera o orçamento do <Spot>"
2. Claude acha o link do Sheet de tipologias em tipologias.js (dashboard/data/tipologias.js)
   → Se o spot já tiver campo `estilo` salvo, usa esse; senão pergunta:
     "Qual o estilo? (1) Clean  (2) Biofílico  (3) Industrial  (4) Bruma"
3. Baixa db002_produtos via Drive → ler_catalogo.py  (preços base)
4. Baixa marcenaria do Sheet de marcenaria (filtrado por estilo + Plus) → dict de peças de marcenaria
5. Lê tipologias do Sheet de tipologias via Drive → lista de Tipologia
6. montar_orcamento.py(tipologias, produtos, marcenaria, estilo="Plus") → lista de MemorialTipologia
7. gerar_sheet.py → cria Sheet de orçamento no Drive + cria Sheet tipologias+custo
8. (opcional) atualiza campo `estilo` do spot em tipologias.js + commit
9. Devolve links dos dois Sheets + resumo (total por tipologia)
```

Gatilhos: "gera o orçamento do <Spot>", "memorial de decor do <Spot>", "orçamento preliminar", `/orcamento-decor`.

---

## Tratamento de erros

| Situação | Comportamento |
|---|---|
| Código do produto não encontrado no catálogo | Inclui a linha com `valor_unitario = 0` e marca `⚠ produto não encontrado` |
| Spot não tem Sheet de tipologias em tipologias.js | Pergunta se quer rodar tabela-tipologias primeiro |
| Drive sem permissão de escrita na pasta | Cria na raiz do Drive e avisa a Raquel pra mover |
| db002_produtos mudou o schema | `ler_catalogo.py` falha com mensagem descritiva das colunas esperadas |

---

## Testes

- `test_ler_catalogo.py` — testa parsing do CSV com fixture de 5 produtos (2 categorias, 1 sem valor)
- `test_montar_orcamento.py`:
  - Cap. 2 sem terraço → sem sofá-cama, sem auxiliar, sem jacuzzi
  - Cap. 4 com garden → com sofá-cama + jacuzzi
  - Cap. 5 com sacada → com sofá-cama + auxiliar + mesa externa
  - PCD → banheiro PCD, sem cama auxiliar
  - Subtotais batem com soma das linhas
  - `total_geral = valor_produtos + taxa_decor + taxa_adm` ✓

---

## Validação de referência

Novo Campeche II (12 tipologias, 49 unidades) — rodar o orçamento e verificar se o valor por tipologia é coerente com o range histórico de spots existentes no sistema de catálogo.

---

## IDs do Drive (referência pra implementação)

| Recurso | ID |
|---|---|
| Catálogo principal (db002_produtos) | `1Q_AiMW7CICEMrpQR3jTchx6xknSEiCQxEZbpm97Yx_o` |
| Marcenaria por estilo | `1VnEZ-2UscCx03cwEGEDVA9vbfaUw4Y04wiM_lh9YRYI` |
| Pasta raiz dos estilos | `1uEBBTJlSUpOh2WxM1GRbx1e932xqI_dy` |
| Pasta estilo CLEAN | `17Nh0A_EsLt1gvwdB-9kcMtTVKkJSsX5O` |
| Pasta estilo BIOFÍLICO | `10HKb-ckaIp_x81LXBvEGevEwIAcmD46H` |
| Pasta estilo INDUSTRIAL | `1XFt6ucRgmmq1PGn4vNxv3tiHuVfmT5Jd` |
| Pasta estilo BRUMA | `19HSW3nsiNcpY5RZNZO4NRguHtXAGgq98` |
| Moodboard CLEAN REV.02 | `1l5nn89FSNder2IFYC835e9aZvVPm6k6WWx9kltbIGjo` |
| Moodboard BIOFÍLICO REV.02 | `1Ti480HgXwdH3piK3vEZ6qmSSCrS0lvP9NwdqvXtustU` |
| Moodboard INDUSTRIAL REV.02 | `1l_S4Yyq5teNGXgxDMwGcwE2dq8g9IpRTGfZy3Fo0bsI` |
| Moodboard BRUMA RV.02 | `1dEvH_cjlHUFMOzQaRgrh212D5WAW6Q1bfy8hPbTyeGU` |

---

## O que NÃO está no escopo

- Imagens dos produtos no memorial (campo fica vazio, como no exemplo)
- Formatação de células no Sheet (sem cores, sem bordas — Drive converte CSV puro)
- Integração com o script existente do catálogo (a skill lê db002_produtos diretamente)
- Personalização por unidade (memorial é por tipologia, não por apartamento)
