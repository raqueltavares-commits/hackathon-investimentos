import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tabela-tipologias" / "scripts"))


def test_fixture_tem_96_unidades(unidades_natal):
    assert len(unidades_natal) == 96
