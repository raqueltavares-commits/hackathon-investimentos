"""Dataclasses compartilhados entre os scripts de orçamento."""
from dataclasses import dataclass, field


@dataclass
class Produto:
    codigo: str
    nome: str
    categoria: str
    valor_unitario: float
    unidade: str = "un"


@dataclass
class LinhaMemorial:
    categoria: str
    item: str
    quantidade: int
    valor_unitario: float
    ambiente: str = ""
    fornecedor: str = "Catálogo Decor"
    referencia: str = ""
    acabamento: str = "A confirmar"
    largura: str = "A confirmar"
    altura: str = "A confirmar"
    profundidade: str = "A confirmar"
    opcional: bool = False  # True = fora do total base (ex: jacuzzi)

    @property
    def valor_total(self) -> float:
        return round(self.quantidade * self.valor_unitario, 2)


@dataclass
class MemorialTipologia:
    tipologia: str
    descricao: str
    estilo: str
    spot: str
    linhas: list[LinhaMemorial] = field(default_factory=list)
    taxa_decor: float = 2500.0

    @property
    def valor_produtos(self) -> float:
        """Soma das linhas NÃO opcionais (base, sem jacuzzi)."""
        return round(sum(l.valor_total for l in self.linhas if not l.opcional), 2)

    @property
    def valor_opcionais(self) -> float:
        """Soma das linhas opcionais (ex: jacuzzi)."""
        return round(sum(l.valor_total for l in self.linhas if l.opcional), 2)

    @property
    def taxa_adm(self) -> float:
        return round(self.valor_produtos * 0.13, 2)

    @property
    def subtotais(self) -> dict[str, float]:
        """Subtotal por categoria, incluindo opcionais (espelha o modelo da Raquel)."""
        result: dict[str, float] = {}
        for l in self.linhas:
            result[l.categoria] = round(result.get(l.categoria, 0.0) + l.valor_total, 2)
        return result

    @property
    def total_geral(self) -> float:
        """Total SEM jacuzzi (headline) = produtos base + taxa decor + taxa adm."""
        return round(self.valor_produtos + self.taxa_decor + self.taxa_adm, 2)

    @property
    def total_com_jacuzzi(self) -> float:
        return round(self.total_geral + self.valor_opcionais, 2)
