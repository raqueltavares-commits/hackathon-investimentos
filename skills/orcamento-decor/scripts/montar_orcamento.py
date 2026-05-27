"""Gera memorial descritivo de decor por tipologia (pacote Plus).

Uso:
  python montar_orcamento.py --tipologias t.json --produtos p.json \
    --estilo clean --spot "Natal Spot"

Entrada:
  --tipologias : JSON lista [{tipologia, terraco, tipo, capacidade}]
  --produtos   : JSON de ler_catalogo.py {codigo: {nome, categoria, valor_unitario}}
  --estilo     : clean | biofilico | industrial | bruma
  --spot       : nome do empreendimento

Saida (stdout): JSON {memoriais: [...], resumo: [...]}
"""
import argparse
import csv as csvmodule
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import LinhaMemorial, MemorialTipologia, Produto

# ---------------------------------------------------------------------------
# Tabela de itens - pacote Plus, precos de referencia 2026
# (role, categoria, codigo_default, descricao, valor_default)
# Precos do catalogo real (db002_produtos) sobrescrevem estes defaults.
# ---------------------------------------------------------------------------
_ITENS_PLUS = [
    # MARCENARIA
    ("gabinete_inferior",   "MARCENARIA",       "MRC0002",  "Gabinete inferior (gavetao como vassoureiro)", 3300.0),
    ("gabinete_superior",   "MARCENARIA",       "MRC0011",  "Gabinete superior com LED",                   1100.0),
    ("cabeceira",           "MARCENARIA",       "MRC0038",  "Cabeceira",                                   5800.0),
    ("arara_roupas",        "MARCENARIA",       "MRC0028",  "Arara de roupas",                             2000.0),
    ("bancada_refeicao",    "MARCENARIA",       "MRC0022",  "Mesa/bancada de refeicao",                     800.0),
    ("movel_apoio",         "MARCENARIA",       "MRC0020",  "Movel de apoio",                              1000.0),
    ("prateleira_banheiro", "MARCENARIA",       "MRC0022b", "Prateleira banheiro",                          450.0),
    # MARMORARIA
    ("bancada_coz_pedra",   "MARMORARIA",       "MRM0007",  "Bancada cozinha (granito pitaya)",            2470.0),
    ("bancada_ban_pedra",   "MARMORARIA",       "MRM0016",  "Bancada banheiro (granito pitaya)",           1499.0),
    # MOBILIARIO
    ("cama_queen",          "MOBILIÁRIO",       "MOB0001",  "Cama box Queen size (c/ auxiliar)",           3986.0),
    ("sofa_cama",           "MOBILIÁRIO",       "MOB0003",  "Sofá-cama",                                   4373.0),
    ("puff",                "MOBILIÁRIO",       "MOB0004",  "Puff",                                         680.0),
    ("cadeira_jantar",      "MOBILIÁRIO",       "MOB0005",  "Cadeira de jantar",                            639.0),
    # LOUCAS E METAIS
    ("torneira_coz",        "LOUÇAS E METAIS",  "LEM0007",  "Torneira de mesa cozinha",                    324.0),
    ("cuba_coz",            "LOUÇAS E METAIS",  "LEM0018",  "Cuba de embutir inox cozinha",                284.0),
    ("cuba_ban",            "LOUÇAS E METAIS",  "LEM0020",  "Cuba de apoio banheiro",                      180.0),
    ("torneira_ban",        "LOUÇAS E METAIS",  "LEM0012",  "Torneira banheiro bica alta",                 289.0),
    ("box_banheiro",        "LOUÇAS E METAIS",  "VDR0004",  "Box reto banheiro",                           983.0),
    ("filtro_agua",         "LOUÇAS E METAIS",  "LEM0027",  "Filtro de agua 3M",                           163.0),
    ("toalheiro_termico",   "LOUÇAS E METAIS",  "LEM0013",  "Toalheiro termico",                           923.0),
    ("kit_metais",          "LOUÇAS E METAIS",  "LEM0001",  "Kit de metais",                               222.0),
    # ELETROS
    ("cooktop",             "ELETROS",          "ELE0006",  "Cooktop vitroceramico 2 bocas",               899.0),
    ("frigobar",            "ELETROS",          "ELE0003",  "Frigobar retro",                             1949.0),
    ("microondas",          "ELETROS",          "ELE0007",  "Microondas 20L Electrolux",                   579.0),
    ("cafeteira",           "ELETROS",          "ELE0019",  "Cafeteira eletrica",                          179.0),
    ("chaleira",            "ELETROS",          "ELE0020",  "Chaleira eletrica",                           189.0),
    ("liquidificador",      "ELETROS",          "ELE0022",  "Liquidificador 1,5L",                         319.0),
    ("depurador",           "ELETROS",          "ELE0014",  "Depurador",                                   799.0),
    ("mini_grill",          "ELETROS",          "ELE0024",  "Mini grill e sanduicheira",                   159.0),
    ("tv",                  "ELETROS",          "ELE0001",  'TV 43"',                                     1599.0),
    # ILUMINACAO
    ("iluminacao",          "ILUMINAÇÃO",       "ILU0001",  "Kit iluminacao",                              347.0),
    # AREA EXTERNA (condicional)
    ("jacuzzi",             "ÁREA EXTERNA",     "EXT0001",  "Jacuzzi circular O 1,80m",                  5000.0),
    ("mesa_externa",        "ÁREA EXTERNA",     "EXT0002",  "Mesa externa redonda + cadeiras",            1500.0),
]

_CADEIRAS_POR_CAP: dict[int, int] = {2: 2, 3: 3, 4: 3, 5: 4}
_TERRACO_GARDEN   = {"garden", "terraço", "terraco"}
_TERRACO_VARANDA  = {"varanda", "sacada"}


def itens_para_tipologia(
    capacidade: int,
    terraco: str,
    tipo: str,
    produtos: dict,
) -> list[LinhaMemorial]:
    t = terraco.strip().lower()
    eh_garden   = t in _TERRACO_GARDEN
    eh_varanda  = t in _TERRACO_VARANDA
    eh_pcd      = tipo.strip().lower() == "pcd"

    linhas: list[LinhaMemorial] = []
    for (role, categoria, codigo, descricao, valor_default) in _ITENS_PLUS:
        if role == "sofa_cama"    and capacidade not in (4, 5): continue
        if role == "jacuzzi"      and not eh_garden:             continue
        if role == "mesa_externa" and not eh_varanda:            continue

        qty = _CADEIRAS_POR_CAP.get(capacidade, 2) if role == "cadeira_jantar" else 1

        if codigo in produtos:
            p = produtos[codigo]
            valor = p.valor_unitario if isinstance(p, Produto) else p.get("valor_unitario", valor_default)
        else:
            valor = valor_default

        nome = f"{descricao} (PCD)" if (
            eh_pcd
            and "banheiro" in descricao.lower()
            and "bancada" not in descricao.lower()
        ) else descricao

        linhas.append(LinhaMemorial(categoria=categoria, item=nome,
                                    quantidade=qty, valor_unitario=valor))
    return linhas


def montar_memorial(
    tipologia: str,
    descricao: str,
    estilo: str,
    spot: str,
    linhas: list[LinhaMemorial],
) -> MemorialTipologia:
    return MemorialTipologia(
        tipologia=tipologia, descricao=descricao,
        estilo=estilo, spot=spot, linhas=linhas,
    )


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def serializar_csv(memorial: MemorialTipologia) -> str:
    out = io.StringIO()
    w = csvmodule.writer(out)

    w.writerow(["TIPOLOGIA:", memorial.tipologia, memorial.descricao])
    w.writerow(["Empreendimento:", memorial.spot])
    w.writerow(["Estilo:", memorial.estilo, "Pacote: Plus"])
    w.writerow([])
    w.writerow(["ITEM", "Quantidade", "Valor Unitario", "Valor Total"])

    cat_atual = None
    for linha in memorial.linhas:
        if linha.categoria != cat_atual:
            cat_atual = linha.categoria
            w.writerow([f" {cat_atual}", "", "", _brl(memorial.subtotais[cat_atual])])
        w.writerow([linha.item, linha.quantidade,
                    _brl(linha.valor_unitario), _brl(linha.valor_total)])

    w.writerow([])
    w.writerow(["", "", "Valor Produtos", _brl(memorial.valor_produtos)])
    w.writerow(["Taxa Decor", "R$", "", _brl(memorial.taxa_decor)])
    w.writerow(["Taxa Adm (13%)", "", "", _brl(memorial.taxa_adm)])
    w.writerow(["TOTAL GERAL", "", "", _brl(memorial.total_geral)])

    return out.getvalue()


def main() -> None:
    p = argparse.ArgumentParser(description="Gera memoriais de decor por tipologia (Plus)")
    p.add_argument("--tipologias", type=Path, required=True,
                   help="JSON com lista [{tipologia, terraco, tipo, capacidade}]")
    p.add_argument("--produtos", type=Path,
                   help="JSON de ler_catalogo.py (omitir = precos default)")
    p.add_argument("--estilo", required=True,
                   choices=["clean", "biofilico", "industrial", "bruma"])
    p.add_argument("--spot", required=True, help="Nome do empreendimento")
    args = p.parse_args()

    tipologias = json.loads(args.tipologias.read_text(encoding="utf-8"))
    produtos: dict = {}
    if args.produtos:
        raw = json.loads(args.produtos.read_text(encoding="utf-8"))
        produtos = {
            k: Produto(k, v["nome"], v["categoria"], v["valor_unitario"], v.get("unidade", "un"))
            for k, v in raw.items()
        }

    memoriais = []
    for t in tipologias:
        letra    = t["tipologia"]
        descr    = f"{t['terraco']} · {t['tipo']} · Cap. {t['capacidade']}"
        linhas   = itens_para_tipologia(t["capacidade"], t["terraco"], t["tipo"], produtos)
        memorial = montar_memorial(letra, descr, args.estilo.capitalize(), args.spot, linhas)
        memoriais.append({
            "tipologia":      letra,
            "descricao":      descr,
            "total_geral":    memorial.total_geral,
            "valor_produtos": memorial.valor_produtos,
            "taxa_adm":       memorial.taxa_adm,
            "taxa_decor":     memorial.taxa_decor,
            "subtotais":      memorial.subtotais,
            "linhas": [
                {"categoria": l.categoria, "item": l.item,
                 "quantidade": l.quantidade, "valor_unitario": l.valor_unitario,
                 "valor_total": l.valor_total}
                for l in memorial.linhas
            ],
            "csv": serializar_csv(memorial),
        })

    resumo = [{"tipologia": m["tipologia"], "descricao": m["descricao"],
               "total_geral": m["total_geral"]} for m in memoriais]
    print(json.dumps({"memoriais": memoriais, "resumo": resumo},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
