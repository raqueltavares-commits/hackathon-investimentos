"""Regras de preço para itens FORA do catálogo Decor (aprendidas do orçamento real
do Rosa Sul — `seazone/rosa-sul-mvp-interiores`).

Itens que o catálogo Supabase não cobre são precificados por uma de duas vias:
1. **Marcenaria sem catálogo** → área (m²) × R$ 2.000/m². A área vem das dimensões do
   Revit (ou estimada). Ex.: painel 9,76 m² → R$ 19.520.
2. **Itens de loja** (sofá, quadros, capacho, plantas, marmoraria) → preço PESQUISADO por
   fornecedor, com link/Referência. Não é fórmula: entra como valor manual + fornecedor +
   link. Plantas/vasos = ARTIFICIAIS do Mercado Livre. Marmoraria = orçamento externo
   (granito, à vista −6%). Não dá pra automatizar — fica como linha com fornecedor/link.

PINTURA: usa o valor do CATÁLOGO Decor (serviço), NÃO uma taxa por m² fixa. (A Raquel
testou R$14/m² mas voltou pro catálogo no memorial final.) Por isso pintura entra como
serviço normal (ver `servicos.py`), não aqui.

Este módulo cobre só a regra de FÓRMULA da marcenaria. As demais são preenchidas como
linhas normais (valor + fornecedor + referência).
"""

TAXA_MARCENARIA_M2 = 2000.0  # R$/m² para marcenaria sem valor no catálogo


def marcenaria_por_m2(area_m2: float, taxa: float = TAXA_MARCENARIA_M2) -> float:
    """Valor de uma peça de marcenaria sem catálogo: área × R$/m²."""
    return round(area_m2 * taxa, 2)
