# Design — Memorial Descritivo Estruturado (evolução da skill orcamento-decor)

**Data:** 2026-05-27
**Projeto:** hackathon-investimentos (trilha Decor)
**Relacionado:** Fase 2 (skill `orcamento-decor`)

---

## Objetivo

Fazer a skill `orcamento-decor` **gerar autonomamente** o memorial descritivo de decor por tipologia na MESMA ESTRUTURA do modelo oficial da Raquel (Sheet exemplo `1-S14JTOVV689UNJAW5lyuv5gDsPOAQq_fG6XEDatj6E`). O exemplo é gabarito de aprendizado — a skill NÃO copia conteúdo, ela **produz** a estrutura a partir dos dados (tipologia + estilo + catálogo interno). Para qualquer Spot futuro, sem intervenção manual.

Escopo escolhido pela Raquel: **estrutura completa do exemplo, populada com os itens que a skill já tem** (~33 itens-núcleo + serviços). Enxoval/utensílios completos ficam pra ela complementar depois.

---

## Estrutura-alvo (extraída do exemplo)

### Colunas (11)
| # | Coluna | Conteúdo |
|---|---|---|
| A | (espaçador) | vazio |
| B | **ITEM/TIPO** | categoria — preenchida só na 1ª linha do bloco da categoria (estilo "célula mesclada") |
| C | **AMBIENTE** | Cozinha · Quarto · Banheiro · Garden · Geral · Serviços — preenchida quando muda |
| D | **IMAGEM** | vazio (placeholder) |
| E | **ITEM** | nome do produto (MAIÚSCULAS), só na 1ª das 4 linhas |
| F | **FICHA TÉCNICA** | rótulo: Largura / Altura / Profundidade / Acabamento |
| G | *(valor da ficha)* | "A confirmar" (dims) ou medida real; Acabamento = material |
| H | **FORNECEDOR** | "Catálogo Decor" (default), 1ª linha |
| I | **QUANT.** | inteiro, 1ª linha |
| J | **REFERÊNCIA** | código do item (ex: MRC0002) ou "Link", 1ª linha |
| K | **VALOR UNITÁRIO** | 1ª linha |
| L | **VALOR TOTAL** | quant × unitário, 1ª linha |

### Linhas
- **Cada item ocupa 4 linhas** (Largura, Altura, Profundidade, Acabamento). Campos do item (categoria, ambiente, nome, fornecedor, quant, ref, valores) só na 1ª linha; as outras 3 têm só rótulo (col F) + valor (col G).
- **TOTAL por categoria**: linha `TOTAL <CATEGORIA>` com o subtotal na coluna VALOR UNITÁRIO (K).
- **Fecho** (após todas as categorias):
  - `Taxa Decor` (R$ 2.500) · `Taxa Adm (13%)`
  - `TOTAL (sem jacuzzi)` ← **total de referência (headline)** — vai pro dashboard
  - `TOTAL (com jacuzzi)` ← alternativa (jacuzzi é exceção por unidade; ex: Bonito só a 113)

### Categorias (ITEM/TIPO), na ordem
MARCENARIA · MOBILIÁRIO · MARMORARIA · METAIS E INOX · ELETROS · ILUMINAÇÃO · INSUMOS (serviços).
(UTENSÍLIOS e DECORAÇÃO/enxoval ficam de fora nesta versão — itens da skill atual.)

---

## Como a skill gera isso (autônomo)

### 1. Catálogo interno enriquecido (`montar_orcamento.py`)
Cada item de `_ITENS_PLUS` ganha campos novos:
```python
@dataclass
class ItemPlus:
    role: str            # gabinete_inferior, ...
    categoria: str       # MARCENARIA | MOBILIÁRIO | MARMORARIA | METAIS E INOX | ELETROS | ILUMINAÇÃO | ÁREA EXTERNA | INSUMOS
    ambiente: str        # Cozinha | Quarto | Banheiro | Garden | Geral | Serviços
    codigo: str          # referência
    nome: str            # MAIÚSCULAS
    valor_default: float
    fornecedor: str = "Catálogo Decor"
```
Dimensões (Largura/Altura/Profundidade) saem "A confirmar" por padrão (igual ao exemplo).

### 2. Acabamento por estilo (paleta embutida)
Novo `references/acabamentos-por-estilo.md` + dict no código: `acabamento[estilo][role] -> str`.
- **Biofílico** calibrado a partir do exemplo (ex: gabinete inferior = "Mdf areia"; gabinete superior = "Mdf sava e palhinha com metal bege claro"; cabeceira = "Mdf savana"; bancadas = "Granito pitaya"; cama = "Suede preto").
- **Clean / Industrial / Bruma**: paleta inicial coerente com o estilo (Clean = madeira clara/neutro; Industrial = metal grafite/concreto; Bruma = tons suaves), marcada como calibrável.
- Fallback: "A confirmar" quando não houver entrada.

### 3. Serviços (categoria INSUMOS) — lista fixa com preço de referência
Instalação elétrica · Instalação hidráulica · Instalação ar-condicionado · Pintura · Feltro nos mobiliários · Limpeza. (Ambiente = Serviços; fornecedor = "Catálogo Decor".)

### 4. Itens condicionais por tipologia (a skill já decide — mantém a lógica atual)
- Sofá-cama: cap 4 e 5.
- Cadeiras: 2/3/3/4 por cap.
- Mesa externa: terraço Sacada/Varanda.
- **Jacuzzi**: terraço Garden/Terraço → entra **só no total "com jacuzzi"**, fora do "sem jacuzzi".
- PCD: sufixo "(PCD)" nos itens de banheiro.

### 5. Serializador
- `serializar_memorial_rows(memorial, estilo) -> list[list]`: produz a matriz das 11 colunas (categoria/ambiente "mescladas", 4 linhas/item, TOTAL por categoria, Taxa Decor/Adm, dois totais).
- `montar_orcamento.py` continua emitindo JSON (com as linhas estruturadas + custo = TOTAL sem jacuzzi pro dashboard).
- A montagem do **.xlsx multi-aba** (uma aba por tipologia + Resumo) usa essa matriz; upload+conversão pra Google Sheet na pasta `03 - Memorial descritivo`.

---

## Impacto no que já existe
- `montar_orcamento.py`: enriquece `_ITENS_PLUS`, adiciona paleta de acabamento, serviços, novo serializador estruturado. `total_geral` passa a ser o **sem jacuzzi**.
- `gerar_dashboard_js.py`: inalterado (usa `total_geral`). Dashboard mostra custo = sem jacuzzi.
- Novo `references/acabamentos-por-estilo.md`.
- Testes: cobrir colunas/linhas da matriz, 4-linhas-por-item, TOTAL por categoria, acabamento por estilo, jacuzzi só no com-jacuzzi, serviços presentes, dois totais.
- O CSV simples antigo (`serializar_csv`) pode ser mantido como fallback ou substituído — decidir no plano.

## Fora de escopo
- Itens de UTENSÍLIOS e DECORAÇÃO/enxoval completos (a Raquel complementa).
- Ler moodboard/marcenaria do Drive em runtime (paleta é embutida, calibrável).
- Imagens na coluna IMAGEM (fica vazia).
- Upload real depende do conector Drive estar na conta da Raquel (bloqueio à parte).
