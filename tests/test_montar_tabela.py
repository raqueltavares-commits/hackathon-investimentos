import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "tabela-tipologias" / "scripts"))


def test_fixture_tem_96_unidades(unidades_natal):
    assert len(unidades_natal) == 96


from montar_tabela import agrupar


def test_agrupar_natal_gera_5_tipologias(unidades_natal):
    tipologias, avisos = agrupar(unidades_natal)
    assert len(tipologias) == 5


def test_agrupar_atribui_letras_sequenciais(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    assert [t["tipologia"] for t in tipologias] == ["A", "B", "C", "D", "E"]


def test_agrupar_maior_grupo_primeiro(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    assert tipologias[0]["quantidade"] == 74
    assert tipologias[0]["capacidade"] == 2
    assert tipologias[0]["terraco"] == "Sem"


def test_agrupar_quantidades_e_atributos(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    chave = {(t["terraco"], t["capacidade"]): t["quantidade"] for t in tipologias}
    assert chave[("Sem", 2)] == 74
    assert chave[("Sem", 5)] == 10
    assert chave[("Sem", 3)] == 10
    assert chave[("Sacada", 5)] == 1
    assert chave[("Sacada", 3)] == 1


def test_agrupar_lista_unidades(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    t_a = next(t for t in tipologias if t["tipologia"] == "A")
    assert len(t_a["unidades"]) == 74
    assert "101" in t_a["unidades"]


def test_agrupar_unidades_em_ordem_numerica():
    unidades = [
        {"unidade": "1001", "pavimento": 10, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.0, "area_unidade": 18.0},
        {"unidade": "101", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.0, "area_unidade": 18.0},
        {"unidade": "102", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.0, "area_unidade": 18.0},
    ]
    tipologias, _ = agrupar(unidades)
    assert tipologias[0]["unidades"] == ["101", "102", "1001"]


def test_agrupar_separa_quando_area_diverge_alem_da_tolerancia():
    # Mesma capacidade/terraço, mas áreas muito diferentes = layouts distintos = tipologias separadas.
    unidades = [
        {"unidade": "1", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.0, "area_unidade": 18.0},
        {"unidade": "2", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.4, "area_unidade": 18.3},
        {"unidade": "3", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 20.0, "area_unidade": 24.0},
    ]
    tipologias, avisos = agrupar(unidades, tolerancia_m2=1.0)
    assert len(tipologias) == 2
    assert sorted(t["quantidade"] for t in tipologias) == [1, 2]
    assert any("layout" in a.lower() for a in avisos)


def test_agrupar_mantem_junto_quando_area_varia_pouco():
    unidades = [
        {"unidade": "1", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.0, "area_unidade": 18.0},
        {"unidade": "2", "pavimento": 1, "terraco": "Sem", "tipo": "Padrão",
         "capacidade": 2, "area_util": 14.6, "area_unidade": 18.4},
    ]
    tipologias, avisos = agrupar(unidades, tolerancia_m2=1.0)
    assert len(tipologias) == 1
    assert tipologias[0]["quantidade"] == 2


from montar_tabela import validar


def test_validar_ok_quando_soma_bate(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    v = validar(tipologias, total_declarado=96)
    assert v["ok"] is True
    assert v["soma"] == 96
    assert v["diff"] == 0


def test_validar_falha_quando_soma_nao_bate(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    v = validar(tipologias, total_declarado=100)
    assert v["ok"] is False
    assert v["soma"] == 96
    assert v["diff"] == -4


from montar_tabela import to_csv


def test_to_csv_tem_cabecalho_e_rodape(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    csv_txt = to_csv(tipologias, total_unidades=96)
    linhas = csv_txt.strip().splitlines()
    assert linhas[0] == (
        "TIPOLOGIA,N DAS UNIDADES,TERRAÇO,TIPO,QUANTIDADE,"
        "CAPACIDADE (previsão),ÁREA ÚTIL (m²),ÁREA DA UNIDADE (m²)"
    )
    linhas = [l for l in csv_txt.strip().splitlines() if l.strip(",").strip()]
    rodape = linhas[-1]
    assert "Total de Tipologias" in rodape and "Total de Unidades" in rodape
    assert "5" in rodape and "96" in rodape


def test_to_csv_capacidade_marcada_como_previsao(unidades_natal):
    tipologias, _ = agrupar(unidades_natal)
    csv_txt = to_csv(tipologias, total_unidades=96)
    assert "previsão" in csv_txt.lower()
