"""Agrupa unidades classificadas em tipologias, valida totais e gera CSV.

Uso (runtime da skill):
    python montar_tabela.py --total 96 < unidades.json

Entrada: JSON (stdin) = lista de unidades classificadas.
Saída: JSON (stdout) = {"tipologias": [...], "validacao": {...}, "csv": "..."}.
"""
import csv
import io
import json
import sys
from collections import defaultdict


_TERRACO_ORDEM = {"Sem": 0, "Sacada": 1, "Varanda": 2, "Garden": 3, "Terraço": 4}


def _ordena_unidades(unidades):
    def chave(u):
        num = u["unidade"]
        try:
            return (0, int(num))
        except (TypeError, ValueError):
            return (1, str(num))
    return sorted(unidades, key=chave)


def _clusters_por_area(us, tolerancia_m2):
    """Quebra um grupo em sub-grupos quando a área útil dá um salto > tolerância.

    Unidades com área quase igual ficam juntas (mesmo layout); um salto grande
    indica layout distinto e abre uma nova tipologia.
    """
    ordenadas = sorted(us, key=lambda u: u["area_util"])
    clusters, atual = [], [ordenadas[0]]
    for u in ordenadas[1:]:
        if u["area_util"] - atual[-1]["area_util"] > tolerancia_m2:
            clusters.append(atual)
            atual = [u]
        else:
            atual.append(u)
    clusters.append(atual)
    return clusters


def agrupar(unidades, tolerancia_m2=1.0):
    """Agrupa unidades em tipologias A, B, C...

    Chave de agrupamento: (terraço, tipo, capacidade). Dentro de cada chave,
    unidades com área útil parecida (diferença <= tolerancia_m2) formam a mesma
    tipologia; um salto maior separa em tipologias diferentes (layouts distintos).
    Ordena por quantidade desc, depois terraço, capacidade asc e área asc.
    Retorna (lista_de_tipologias, lista_de_avisos).
    """
    grupos = defaultdict(list)
    for u in unidades:
        grupos[(u["terraco"], u["tipo"], u["capacidade"])].append(u)

    itens = []
    for (terraco, tipo, capacidade), us in grupos.items():
        clusters = _clusters_por_area(us, tolerancia_m2)
        for cl in clusters:
            areas_uteis = [u["area_util"] for u in cl]
            areas_unid = [u["area_unidade"] for u in cl]
            itens.append({
                "terraco": terraco,
                "tipo": tipo,
                "capacidade": capacidade,
                "quantidade": len(cl),
                "unidades": [u["unidade"] for u in _ordena_unidades(cl)],
                "area_util_min": min(areas_uteis),
                "area_util_max": max(areas_uteis),
                "area_unidade_min": min(areas_unid),
                "area_unidade_max": max(areas_unid),
                "_n_clusters": len(clusters),
            })

    itens.sort(key=lambda t: (
        -t["quantidade"],
        _TERRACO_ORDEM.get(t["terraco"], 99),
        t["capacidade"],
        t["area_util_min"],
    ))

    avisos = []
    for i, t in enumerate(itens):
        t["tipologia"] = chr(ord("A") + i)
    for t in itens:
        if t.pop("_n_clusters", 1) > 1:
            avisos.append(
                f"Tipologia {t['tipologia']}: mesma capacidade ({t['capacidade']}) e "
                f"terraço ({t['terraco']}) de outra(s), mas área útil distinta "
                f"(~{t['area_util_min']:.2f} m²) — layouts diferentes, separados."
            )
    return itens, avisos


def validar(tipologias, total_declarado):
    """Confere se a soma das quantidades bate com o total declarado no anteprojeto."""
    soma = sum(t["quantidade"] for t in tipologias)
    diff = soma - total_declarado
    return {
        "ok": diff == 0,
        "soma": soma,
        "total_declarado": total_declarado,
        "diff": diff,
    }


def _fmt_area(mn, mx):
    return f"{mn:.2f}" if abs(mx - mn) < 0.01 else f"{mn:.2f}–{mx:.2f}"


def to_csv(tipologias, total_unidades):
    """Gera o CSV da tabela de tipologias (cabeçalho + linhas + rodapé)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "TIPOLOGIA", "N DAS UNIDADES", "TERRAÇO", "TIPO", "QUANTIDADE",
        "CAPACIDADE (previsão)", "ÁREA ÚTIL (m²)", "ÁREA DA UNIDADE (m²)",
    ])
    for t in tipologias:
        w.writerow([
            t["tipologia"],
            ", ".join(t["unidades"]),
            t["terraco"],
            t["tipo"],
            t["quantidade"],
            t["capacidade"],
            _fmt_area(t["area_util_min"], t["area_util_max"]),
            _fmt_area(t["area_unidade_min"], t["area_unidade_max"]),
        ])
    w.writerow([])
    w.writerow([
        "Total de Tipologias", len(tipologias), "", "",
        "Total de Unidades", total_unidades, "", "",
    ])
    return buf.getvalue()


def main(argv=None):
    import argparse
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Monta a tabela de tipologias.")
    p.add_argument("--total", type=int, required=True,
                   help="Total de unidades declarado no anteprojeto.")
    p.add_argument("--tolerancia", type=float, default=1.0,
                   help="Tolerância de variação de área útil (m²) dentro de uma tipologia.")
    args = p.parse_args(argv)

    unidades = json.load(sys.stdin)
    tipologias, avisos = agrupar(unidades, tolerancia_m2=args.tolerancia)
    validacao = validar(tipologias, total_declarado=args.total)
    csv_txt = to_csv(tipologias, total_unidades=args.total)
    json.dump(
        {"tipologias": tipologias, "validacao": validacao,
         "avisos": avisos, "csv": csv_txt},
        sys.stdout, ensure_ascii=False, indent=2,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
