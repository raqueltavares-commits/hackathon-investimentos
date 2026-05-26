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
