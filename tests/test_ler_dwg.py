import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tabela-tipologias" / "scripts"))

from ler_dwg import ExtraidosDWG


def test_conta_esquadrias_por_unidade_exemplo_simples():
    """Unidades 101 e 102: cada uma com 2 janelas."""
    extraidos = ExtraidosDWG(
        unidades={"101": [("V1", (0, 0)), ("V2", (1, 1))],
                  "102": [("V3", (0, 5)), ("V4", (1, 6))]},
        poligonos={},
    )
    contagem = extraidos.contagem_por_unidade()
    assert contagem["101"] == 2
    assert contagem["102"] == 2


def test_esquadrias_diferentes_separam_tipologias():
    extraidos = ExtraidosDWG(
        unidades={"101": [("V1", (0, 0))],  # 1 esquadria
                  "102": [("V2", (0, 5)), ("V3", (1, 6))]},  # 2 esquadrias
        poligonos={},
    )
    contagem = extraidos.contagem_por_unidade()
    assert contagem["101"] == 1
    assert contagem["102"] == 2
