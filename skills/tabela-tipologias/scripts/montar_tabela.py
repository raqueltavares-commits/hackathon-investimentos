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


def agrupar(unidades, tolerancia_m2=1.0):
    """Agrupa unidades por (terraco, tipo, capacidade) em tipologias A, B, C...

    Ordena por quantidade desc, depois terraco, depois capacidade asc.
    Sinaliza em `avisos` grupos cuja área útil varia além de `tolerancia_m2`.
    Retorna (lista_de_tipologias, lista_de_avisos).
    """
    grupos = defaultdict(list)
    for u in unidades:
        grupos[(u["terraco"], u["tipo"], u["capacidade"])].append(u)

    itens = []
    for (terraco, tipo, capacidade), us in grupos.items():
        areas_uteis = [u["area_util"] for u in us]
        areas_unid = [u["area_unidade"] for u in us]
        itens.append({
            "terraco": terraco,
            "tipo": tipo,
            "capacidade": capacidade,
            "quantidade": len(us),
            "unidades": [u["unidade"] for u in us],
            "area_util_min": min(areas_uteis),
            "area_util_max": max(areas_uteis),
            "area_unidade_min": min(areas_unid),
            "area_unidade_max": max(areas_unid),
        })

    itens.sort(key=lambda t: (
        -t["quantidade"],
        _TERRACO_ORDEM.get(t["terraco"], 99),
        t["capacidade"],
    ))

    avisos = []
    for i, t in enumerate(itens):
        t["tipologia"] = chr(ord("A") + i)
        if t["area_util_max"] - t["area_util_min"] > tolerancia_m2:
            avisos.append(
                f"Tipologia {t['tipologia']}: área útil varia de "
                f"{t['area_util_min']:.2f} a {t['area_util_max']:.2f} m² "
                f"(> {tolerancia_m2} m²) — conferir se são o mesmo layout."
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
    w.writerow(["Total de Tipologias", len(tipologias)])
    w.writerow(["Total de Unidades", total_unidades])
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
