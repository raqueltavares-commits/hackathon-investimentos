import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from precos_fora_catalogo import marcenaria_por_m2, TAXA_MARCENARIA_M2


def test_taxa_marcenaria_default():
    assert TAXA_MARCENARIA_M2 == 2000.0


def test_marcenaria_por_m2():
    # painel recepção Rosa Sul: 9,76 m² × R$2.000 = R$19.520
    assert marcenaria_por_m2(9.76) == 19520.0


def test_marcenaria_taxa_custom():
    assert marcenaria_por_m2(2.0, taxa=2500.0) == 5000.0
