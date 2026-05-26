import pytest

TERRACO_SEM, TERRACO_SACADA = "Sem", "Sacada"
TIPO_PADRAO = "Padrão"


def _unidades(n, terraco, tipo, capacidade, area_util, area_unidade, start=1):
    return [
        {
            "unidade": str(start + i),
            "pavimento": (start + i) // 100,
            "terraco": terraco,
            "tipo": tipo,
            "capacidade": capacidade,
            "area_util": area_util,
            "area_unidade": area_unidade,
        }
        for i in range(n)
    ]


@pytest.fixture
def unidades_natal():
    """Natal Spot: 96 unidades, 5 tipologias (verdade conhecida do anteprojeto)."""
    return (
        _unidades(74, TERRACO_SEM, TIPO_PADRAO, 2, 14.33, 18.50, start=101)
        + _unidades(10, TERRACO_SEM, TIPO_PADRAO, 5, 19.94, 24.00, start=201)
        + _unidades(10, TERRACO_SEM, TIPO_PADRAO, 3, 15.18, 19.00, start=301)
        + _unidades(1, TERRACO_SACADA, TIPO_PADRAO, 5, 15.18, 22.00, start=407)
        + _unidades(1, TERRACO_SACADA, TIPO_PADRAO, 3, 15.10, 21.50, start=408)
    )
