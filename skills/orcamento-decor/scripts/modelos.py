"""Dataclasses compartilhados entre os scripts de orçamento."""
from dataclasses import dataclass, field

TAXA_ADM_PCT = 0.13    # incide só na ÁREA COMUM
TAXA_DECOR_PCT = 0.06  # variável: incide nas duas (área comum + unidades) quando tem


@dataclass
class Produto:
    codigo: str
    nome: str
    categoria: str
    valor_unitario: float
    unidade: str = "un"
    cor_acabamento: str = ""
    link: str = ""


@dataclass
class LinhaMemorial:
    categoria: str
    item: str
    quantidade: int
    valor_unitario: float
    ambiente: str = ""
    fornecedor: str = "Catálogo Decor"
    referencia: str = ""
    cor_acabamento: str = "A definir"
    frete: float = 0.0
    acabamento: str = "A confirmar"
    largura: str = "A confirmar"
    altura: str = "A confirmar"
    profundidade: str = "A confirmar"
    opcional: bool = False  # True = fora do total base (ex: jacuzzi)

    @property
    def valor_total(self) -> float:
        return round(self.quantidade * self.valor_unitario, 2)

    @property
    def total_linha(self) -> float:
        """Total real da linha = valor total + frete (espelha 'Total + Frete')."""
        return round(self.valor_total + self.frete, 2)


@dataclass
class MemorialTipologia:
    tipologia: str
    descricao: str
    estilo: str
    spot: str
    linhas: list[LinhaMemorial] = field(default_factory=list)
    tem_decor: bool = True       # quando False, a Taxa Decor fica zerada (linha mantida)
    incluir_adm: bool = False    # unidades NÃO levam ADM; área comum leva

    @property
    def valor_produtos(self) -> float:
        """Soma das linhas NÃO opcionais, já com frete (base, sem jacuzzi)."""
        return round(sum(l.total_linha for l in self.linhas if not l.opcional), 2)

    @property
    def valor_opcionais(self) -> float:
        """Soma das linhas opcionais (ex: jacuzzi), já com frete."""
        return round(sum(l.total_linha for l in self.linhas if l.opcional), 2)

    @property
    def taxa_decor(self) -> float:
        return round(self.valor_produtos * TAXA_DECOR_PCT, 2) if self.tem_decor else 0.0

    @property
    def taxa_adm(self) -> float:
        return round(self.valor_produtos * TAXA_ADM_PCT, 2) if self.incluir_adm else 0.0

    @property
    def subtotais(self) -> dict[str, float]:
        """Subtotal por categoria (com frete), incluindo opcionais (espelha o modelo)."""
        result: dict[str, float] = {}
        for l in self.linhas:
            result[l.categoria] = round(result.get(l.categoria, 0.0) + l.total_linha, 2)
        return result

    @property
    def total_geral(self) -> float:
        """Total SEM jacuzzi (headline) = produtos base + taxa decor + taxa adm."""
        return round(self.valor_produtos + self.taxa_decor + self.taxa_adm, 2)

    @property
    def total_com_jacuzzi(self) -> float:
        return round(self.total_geral + self.valor_opcionais, 2)
