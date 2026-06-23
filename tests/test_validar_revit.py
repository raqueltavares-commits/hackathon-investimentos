import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/tabela-tipologias/scripts"))

from validar_revit import validar, capacidade_por_area, TOL_AREA_PADRAO


def test_tolerancia_padrao():
    assert TOL_AREA_PADRAO == 0.5


def test_capacidade_por_area_matriz():
    assert capacidade_por_area(16.84) == 2
    assert capacidade_por_area(18.16) == 3
    assert capacidade_por_area(20.0) == 4
    assert capacidade_por_area(23.46) == 5


def test_capacidade_pcd_reduz_um_nivel():
    assert capacidade_por_area(18.16, pcd=True) == 2  # cap3 - 1


def test_area_dentro_da_tolerancia_ok():
    unid = [{"unidade": "101", "capacidade": 2, "area_util": 16.84}]
    rev = [{"unidade": "101", "area_revit": 17.0}]
    r = validar(unid, rev)
    v = r["validacoes"][0]
    assert v["area_ok"] is True
    assert v["capacidade_ok"] is True
    assert r["ok"] is True
    assert r["divergencias"] == []


def test_area_divergente_sinaliza():
    unid = [{"unidade": "108", "capacidade": 3, "area_util": 18.16}]
    rev = [{"unidade": "108", "area_revit": 23.46}]
    r = validar(unid, rev)
    v = r["validacoes"][0]
    assert v["area_ok"] is False
    assert v["capacidade_ok"] is False          # 23,46 → cap5, não cap3
    assert v["cap_revit"] == 5
    assert any("108" in d for d in r["divergencias"])
    assert r["ok"] is False


def test_contagem_unidades():
    unid = [{"unidade": "101", "capacidade": 2, "area_util": 16.0},
            {"unidade": "102", "capacidade": 2, "area_util": 16.0}]
    rev = [{"unidade": "101", "area_revit": 16.0}]  # falta a 102 no Revit
    r = validar(unid, rev)
    assert r["contagem"]["classificadas"] == 2
    assert r["contagem"]["revit"] == 1
    assert "102" in r["sem_match_revit"]
    assert r["ok"] is False


def test_sem_revit_pula():
    unid = [{"unidade": "101", "capacidade": 2, "area_util": 16.0}]
    r = validar(unid, [])
    assert r["pulado"] is True
    assert r["ok"] is True
