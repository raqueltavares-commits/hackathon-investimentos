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

    @property
    def valor_total(self) -> float:
        return round(self.quantidade * self.valor_unitario, 2)


@dataclass
class MemorialTipologia:
    tipologia: str   # ex: "A"
    descricao: str   # ex: "Sem Sacada · Padrão · Cap. 4"
    estilo: str      # ex: "Clean"
    spot: str        # ex: "Natal Spot"
    linhas: list[LinhaMemorial] = field(default_factory=list)
    taxa_decor: float = 2500.0

    @property
    def valor_produtos(self) -> float:
        return round(sum(l.valor_total for l in self.linhas), 2)

    @property
    def taxa_adm(self) -> float:
        return round(self.valor_produtos * 0.13, 2)

    @property
    def subtotais(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for l in self.linhas:
            result[l.categoria] = round(result.get(l.categoria, 0.0) + l.valor_total, 2)
        return result

    @property
    def total_geral(self) -> float:
        return round(self.valor_produtos + self.taxa_decor + self.taxa_adm, 2)
