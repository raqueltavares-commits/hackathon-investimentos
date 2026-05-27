import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skills/orcamento-decor/scripts"))

from ler_catalogo import parsear_csv
from modelos import Produto

FIXTURE = (Path(__file__).parent / "fixtures/catalogo_sample.csv").read_text(encoding="utf-8")


def test_parseia_produto_marcenaria():
    produtos = parsear_csv(FIXTURE)
    assert "MRC0002" in produtos
    p = produtos["MRC0002"]
    assert p.nome == "Gabinete inferior"
    assert p.categoria == "MARCENARIA"
    assert p.valor_unitario == 3300.0
    assert p.unidade == "un"


def test_parseia_todos_os_codigos():
    produtos = parsear_csv(FIXTURE)
    assert set(produtos.keys()) == {"MRC0002", "MOB0001", "ELE0006", "LEM0007",
                                    "SEM_PRECO", "REAIS"}


def test_valor_ausente_vira_zero():
    produtos = parsear_csv(FIXTURE)
    assert produtos["SEM_PRECO"].valor_unitario == 0.0


def test_aceita_valor_formatado_em_reais():
    produtos = parsear_csv(FIXTURE)
    assert produtos["REAIS"].valor_unitario == 1234.56


def test_erro_se_coluna_obrigatoria_ausente():
    import pytest
    csv_ruim = "nome,valor\nItem A,100\n"
    with pytest.raises(ValueError, match="Colunas não encontradas"):
        parsear_csv(csv_ruim)


def test_mapeamento_manual_de_colunas():
    csv_custom = "Ref,Produto,Grupo,Preco\nXX01,Mesa,MOBILIÁRIO,500.00\n"
    produtos = parsear_csv(csv_custom, {
        "codigo": "Ref", "nome": "Produto",
        "categoria": "Grupo", "valor_unitario": "Preco",
    })
    assert "XX01" in produtos
    assert produtos["XX01"].valor_unitario == 500.0
