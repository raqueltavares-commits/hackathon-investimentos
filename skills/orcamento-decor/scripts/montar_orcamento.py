"""Gera memorial descritivo de decor por tipologia (pacote Plus), estrutura oficial.

Uso:
  python montar_orcamento.py --tipologias t.json --produtos p.json \
    --estilo biofilico --spot "Bonito Spot"

Saida (stdout): JSON {memoriais: [...], resumo: [...]}
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import LinhaMemorial, MemorialTipologia, Produto
from acabamentos import acabamento_de, META_ITEM
from servicos import SERVICOS

# (role, categoria, codigo_default, descricao, valor_default)
_ITENS_PLUS = [
    ("gabinete_inferior",   "MARCENARIA",      "MRC0002",  "Gabinete inferior (gavetão como vassoureiro)", 3300.0),
    ("gabinete_superior",   "MARCENARIA",      "MRC0011",  "Gabinete superior com LED",                   1100.0),
    ("cabeceira",           "MARCENARIA",      "MRC0038",  "Cabeceira",                                   5800.0),
    ("arara_roupas",        "MARCENARIA",      "MRC0028",  "Arara de roupas",                             2000.0),
    ("bancada_refeicao",    "MARCENARIA",      "MRC0022",  "Mesa/bancada de refeição",                     800.0),
    ("movel_apoio",         "MARCENARIA",      "MRC0020",  "Móvel de apoio",                              1000.0),
    ("prateleira_banheiro", "MARCENARIA",      "MRC0022b", "Prateleira banheiro",                          450.0),
    ("bancada_coz_pedra",   "MARMORARIA",      "MRM0007",  "Bancada cozinha",                             2470.0),
    ("bancada_ban_pedra",   "MARMORARIA",      "MRM0016",  "Bancada banheiro",                            1499.0),
    ("cama_queen",          "MOBILIÁRIO",      "MOB0001",  "Cama box Queen size (c/ auxiliar)",           3986.0),
    ("sofa_cama",           "MOBILIÁRIO",      "MOB0003",  "Sofá-cama",                                   4373.0),
    ("puff",                "MOBILIÁRIO",      "MOB0004",  "Puff",                                         680.0),
    ("cadeira_jantar",      "MOBILIÁRIO",      "MOB0005",  "Cadeira de jantar",                            639.0),
    ("torneira_coz",        "METAIS E INOX",   "LEM0007",  "Torneira de mesa cozinha",                    324.0),
    ("cuba_coz",            "METAIS E INOX",   "LEM0018",  "Cuba de embutir inox cozinha",                284.0),
    ("cuba_ban",            "METAIS E INOX",   "LEM0020",  "Cuba de apoio banheiro",                      180.0),
    ("torneira_ban",        "METAIS E INOX",   "LEM0012",  "Torneira banheiro bica alta",                 289.0),
    ("box_banheiro",        "METAIS E INOX",   "VDR0004",  "Box reto banheiro",                           983.0),
    ("filtro_agua",         "METAIS E INOX",   "LEM0027",  "Filtro de água 3M",                           163.0),
    ("toalheiro_termico",   "METAIS E INOX",   "LEM0013",  "Toalheiro térmico",                           923.0),
    ("kit_metais",          "METAIS E INOX",   "LEM0001",  "Kit de metais",                               222.0),
    ("cooktop",             "ELETROS",         "ELE0006",  "Cooktop vitrocerâmico 2 bocas",               899.0),
    ("frigobar",            "ELETROS",         "ELE0003",  "Frigobar retrô",                             1949.0),
    ("microondas",          "ELETROS",         "ELE0007",  "Microondas 20L Electrolux",                   579.0),
    ("cafeteira",           "ELETROS",         "ELE0019",  "Cafeteira elétrica",                          179.0),
    ("chaleira",            "ELETROS",         "ELE0020",  "Chaleira elétrica",                           189.0),
    ("liquidificador",      "ELETROS",         "ELE0022",  "Liquidificador 1,5L",                         319.0),
    ("depurador",           "ELETROS",         "ELE0014",  "Depurador",                                   799.0),
    ("mini_grill",          "ELETROS",         "ELE0024",  "Mini grill e sanduicheira",                   159.0),
    ("tv",                  "ELETROS",         "ELE0001",  'Smart TV 43"',                               1599.0),
    ("iluminacao",          "ILUMINAÇÃO",      "ILU0001",  "Kit iluminação",                              347.0),
    ("jacuzzi",             "ÁREA EXTERNA",    "EXT0001",  "Jacuzzi circular Ø 1,80m",                  5000.0),
    ("mesa_externa",        "ÁREA EXTERNA",    "EXT0002",  "Mesa externa redonda + cadeiras",            1500.0),
]

_CADEIRAS_POR_CAP: dict[int, int] = {2: 2, 3: 3, 4: 3, 5: 4}
_TERRACO_GARDEN  = {"garden", "terraço", "terraco"}
_TERRACO_VARANDA = {"varanda", "sacada"}

_COLUNAS = ["", "ITEM/TIPO", "AMBIENTE", "IMAGEM", "ITEM", "FICHA TÉCNICA", "",
            "FORNECEDOR", "QUANT.", "REFERÊNCIA", "VALOR UNITÁRIO", "VALOR TOTAL"]


def itens_para_tipologia(
    capacidade: int,
    terraco: str,
    tipo: str,
    produtos: dict,
    estilo: str = "biofilico",
) -> list[LinhaMemorial]:
    t = terraco.strip().lower()
    eh_garden  = t in _TERRACO_GARDEN
    eh_varanda = t in _TERRACO_VARANDA
    eh_pcd     = tipo.strip().lower() == "pcd"

    linhas: list[LinhaMemorial] = []
    for (role, categoria, codigo, descricao, valor_default) in _ITENS_PLUS:
        if role == "sofa_cama"    and capacidade not in (4, 5): continue
        if role == "jacuzzi"      and not eh_garden:            continue
        if role == "mesa_externa" and not eh_varanda:           continue

        qty = _CADEIRAS_POR_CAP.get(capacidade, 2) if role == "cadeira_jantar" else 1

        if codigo in produtos:
            p = produtos[codigo]
            valor = p.valor_unitario if isinstance(p, Produto) else p.get("valor_unitario", valor_default)
        else:
            valor = valor_default

        nome = f"{descricao} (PCD)" if (
            eh_pcd and "banheiro" in descricao.lower() and "bancada" not in descricao.lower()
        ) else descricao

        linhas.append(LinhaMemorial(
            categoria=categoria, item=nome, quantidade=qty, valor_unitario=valor,
            ambiente=META_ITEM.get(role, {}).get("ambiente", ""),
            referencia=codigo, acabamento=acabamento_de(estilo, role),
            opcional=(role == "jacuzzi"),
        ))

    for (role, nome, ambiente, codigo, valor_default) in SERVICOS:
        linhas.append(LinhaMemorial(
            categoria="INSUMOS", item=nome, quantidade=1, valor_unitario=valor_default,
            ambiente=ambiente, referencia=codigo, acabamento="N/A",
        ))
    return linhas


def montar_memorial(tipologia, descricao, estilo, spot, linhas) -> MemorialTipologia:
    return MemorialTipologia(tipologia=tipologia, descricao=descricao,
                             estilo=estilo, spot=spot, linhas=linhas)


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def serializar_estruturado(memorial: MemorialTipologia, estilo: str) -> list[list]:
    """Matriz de 11 colunas no formato oficial (categoria/ambiente 'mescladas',
    4 linhas por item, TOTAL por categoria, taxas e dois totais)."""
    rows: list[list] = []
    rows.append(["", "MEMORIAL DESCRITIVO", memorial.spot, "", "",
                 f"{memorial.tipologia} — {memorial.descricao}", "", "",
                 f"Estilo: {memorial.estilo}", "Pacote: Plus", "", ""])
    rows.append(list(_COLUNAS))

    cat_atual = None
    amb_atual = None
    for l in memorial.linhas:
        cat_cell = ""
        amb_cell = ""
        if l.categoria != cat_atual:
            cat_atual = l.categoria
            amb_atual = None
            cat_cell = l.categoria
        if l.ambiente != amb_atual:
            amb_atual = l.ambiente
            amb_cell = l.ambiente
        rows.append(["", cat_cell, amb_cell, "", l.item, "Largura", l.largura,
                     l.fornecedor, l.quantidade, l.referencia,
                     _brl(l.valor_unitario), _brl(l.valor_total)])
        rows.append(["", "", "", "", "", "Altura", l.altura, "", "", "", "", ""])
        rows.append(["", "", "", "", "", "Profundidade", l.profundidade, "", "", "", "", ""])
        rows.append(["", "", "", "", "", "Acabamento", l.acabamento, "", "", "", "", ""])

    vistas: list[str] = []
    for l in memorial.linhas:
        if l.categoria not in vistas:
            vistas.append(l.categoria)
    rows.append([""] * 12)
    for cat in vistas:
        rows.append(["", f"TOTAL {cat}", "", "", "", "", "", "", "", "",
                     _brl(memorial.subtotais[cat]), ""])

    tem_opcionais = memorial.valor_opcionais > 0
    rows.append([""] * 12)
    rows.append(["", "Valor Produtos" + (" (sem jacuzzi)" if tem_opcionais else ""),
                 "", "", "", "", "", "", "", "", _brl(memorial.valor_produtos), ""])
    rows.append(["", "Taxa Decor", "", "", "", "", "", "", "", "", _brl(memorial.taxa_decor), ""])
    rows.append(["", "Taxa Adm (13%)", "", "", "", "", "", "", "", "", _brl(memorial.taxa_adm), ""])
    rows.append(["", "TOTAL (sem jacuzzi)" if tem_opcionais else "TOTAL GERAL",
                 "", "", "", "", "", "", "", "", _brl(memorial.total_geral), ""])
    if tem_opcionais:
        rows.append(["", "TOTAL (com jacuzzi)", "", "", "", "", "", "", "", "",
                     _brl(memorial.total_com_jacuzzi), ""])
    return rows


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Gera memoriais de decor por tipologia (Plus)")
    p.add_argument("--tipologias", type=Path, required=True)
    p.add_argument("--produtos", type=Path)
    p.add_argument("--estilo", required=True, choices=["clean", "biofilico", "industrial", "bruma"])
    p.add_argument("--spot", required=True)
    args = p.parse_args()

    tipologias = json.loads(args.tipologias.read_text(encoding="utf-8"))
    produtos: dict = {}
    if args.produtos:
        raw = json.loads(args.produtos.read_text(encoding="utf-8"))
        produtos = {k: Produto(k, v["nome"], v["categoria"], v["valor_unitario"], v.get("unidade", "un"))
                    for k, v in raw.items()}

    memoriais = []
    for t in tipologias:
        letra = t["tipologia"]
        terraco_label = "Sem terraço" if t["terraco"].strip().lower() == "sem" else t["terraco"]
        descr = f"{terraco_label} · {t['tipo']} · Cap. {t['capacidade']}"
        linhas = itens_para_tipologia(t["capacidade"], t["terraco"], t["tipo"], produtos,
                                      estilo=args.estilo)
        m = montar_memorial(letra, descr, args.estilo.capitalize(), args.spot, linhas)
        memoriais.append({
            "tipologia": letra, "descricao": descr,
            "total_geral": m.total_geral, "total_com_jacuzzi": m.total_com_jacuzzi,
            "valor_produtos": m.valor_produtos, "valor_opcionais": m.valor_opcionais,
            "taxa_adm": m.taxa_adm, "taxa_decor": m.taxa_decor, "subtotais": m.subtotais,
            "linhas": [
                {"categoria": l.categoria, "ambiente": l.ambiente, "item": l.item,
                 "quantidade": l.quantidade, "valor_unitario": l.valor_unitario,
                 "valor_total": l.valor_total, "referencia": l.referencia,
                 "acabamento": l.acabamento, "fornecedor": l.fornecedor, "opcional": l.opcional}
                for l in m.linhas
            ],
            "rows": serializar_estruturado(m, args.estilo),
        })

    resumo = [{"tipologia": x["tipologia"], "descricao": x["descricao"],
               "total_geral": x["total_geral"]} for x in memoriais]
    print(json.dumps({"memoriais": memoriais, "resumo": resumo}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
