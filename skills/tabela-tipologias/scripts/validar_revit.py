"""Valida a tabela de tipologias contra o modelo Revit aberto (passo OPCIONAL).

O Revit é COMPLEMENTO — a fonte da tabela é o anteprojeto LANÇAMENTOS. Aqui só
SINALIZAMOS divergências (área/capacidade/contagem) pra Raquel decidir; nada é
corrigido automaticamente.

A skill (agente) coleta via MCP, por nível de unidades:
- Rooms (OST_Rooms -2000160): Number/Name + Área → {unidade, area_revit}.
Monta `revit.json`: {"unidades": [{"unidade":"101","area_revit":16.84}, ...]}.

Uso:
  python validar_revit.py --unidades unidades.json --revit revit.json [--tol 0.5]
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

TOL_AREA_PADRAO = 0.5  # m² — Δ acima disso vira alerta (confirmado pela Raquel)


def capacidade_por_area(area: float, pcd: bool = False) -> int:
    """Matriz de capacidade pela área interna (privativa coberta), espelhando a regra
    do projeto: <=17 m²=2; ~18=3; ~19-21=4; >=22=5. PCD reduz 1 nível (mín. 2)."""
    if area <= 17.0:
        cap = 2
    elif area <= 18.5:
        cap = 3
    elif area < 22.0:
        cap = 4
    else:
        cap = 5
    if pcd:
        cap = max(2, cap - 1)
    return cap


def _num(u) -> str:
    return str(u).strip()


def validar(unidades: list[dict], revit_unidades: list[dict],
            tol_area: float = TOL_AREA_PADRAO) -> dict:
    """Casa por número de unidade. Devolve validações + divergências (não corrige)."""
    if not revit_unidades:
        return {"pulado": True, "ok": True, "validacoes": [], "divergencias": [],
                "contagem": {"classificadas": len(unidades), "revit": 0, "ok": None},
                "sem_match_revit": [], "sem_match_classificacao": [], "esquadrias_por_grupo": []}

    rev_por_num = {_num(r["unidade"]): r for r in revit_unidades}
    classif_nums = {_num(u["unidade"]) for u in unidades}

    validacoes: list[dict] = []
    divergencias: list[str] = []
    sem_match_revit: list[str] = []

    for u in unidades:
        num = _num(u["unidade"])
        rev = rev_por_num.get(num)
        if rev is None:
            sem_match_revit.append(num)
            continue
        area_util = float(u.get("area_util") or 0.0)
        area_revit = float(rev.get("area_revit") or 0.0)
        delta = round(area_revit - area_util, 2)
        area_ok = abs(delta) <= tol_area
        pcd = str(u.get("tipo", "")).strip().lower() == "pcd"
        cap_revit = capacidade_por_area(area_revit, pcd=pcd)
        cap_classif = int(u.get("capacidade") or 0)
        capacidade_ok = cap_revit == cap_classif

        validacoes.append({
            "unidade": num, "area_util": area_util, "area_revit": area_revit,
            "delta_area": delta, "area_ok": area_ok,
            "cap_classificada": cap_classif, "cap_revit": cap_revit,
            "capacidade_ok": capacidade_ok,
        })
        if not area_ok:
            divergencias.append(
                f"{num}: área Revit {area_revit:.2f} m² vs anteprojeto {area_util:.2f} m² "
                f"(Δ {delta:+.2f}).")
        if not capacidade_ok:
            divergencias.append(
                f"{num}: capacidade pela área do Revit = {cap_revit} (classificada {cap_classif}) "
                f"→ revisar.")

    # Fase 2 — esquadrias por grupo (janela = sinal principal; porta = apoio).
    # Agrupa pelo mesmo critério do montar_tabela (terraço+tipo+capacidade+área); dentro de
    # cada grupo, nº de janelas diferente sinaliza possível tipologia separada (ex.: esquina).
    grupos: dict[tuple, list] = {}
    for u in unidades:
        rev = rev_por_num.get(_num(u["unidade"]))
        if not rev or rev.get("janelas") is None:
            continue
        key = (str(u.get("terraco", "")).strip().lower(), str(u.get("tipo", "")).strip().lower(),
               int(u.get("capacidade") or 0), round(float(u.get("area_util") or 0.0), 2))
        grupos.setdefault(key, []).append((_num(u["unidade"]), int(rev["janelas"])))

    esquadrias_por_grupo: list[dict] = []
    for (terraco, tipo, cap, area), membros in grupos.items():
        counts = [j for _n, j in membros]
        distintos = sorted(set(counts))
        consistente = len(distintos) <= 1
        label = f"{terraco or 'sem'}·{tipo}·cap{cap}·{area:g}m²"
        esquadrias_por_grupo.append({
            "grupo": label, "janelas": distintos, "consistente": consistente,
            "unidades": {n: j for n, j in membros},
        })
        if not consistente:
            modo = Counter(counts).most_common(1)[0][0]
            odd = [n for n, j in membros if j != modo]
            divergencias.append(
                f"Grupo {label}: nº de janelas varia {distintos} — {', '.join(odd)} "
                f"difere(m) → possível tipologia separada.")

    sem_match_classificacao = sorted(set(rev_por_num) - classif_nums)
    contagem = {"classificadas": len(unidades), "revit": len(revit_unidades),
                "ok": len(unidades) == len(revit_unidades)
                      and not sem_match_revit and not sem_match_classificacao}
    ok = (not divergencias and contagem["ok"]
          and not sem_match_revit and not sem_match_classificacao)
    return {"pulado": False, "ok": ok, "validacoes": validacoes,
            "divergencias": divergencias, "contagem": contagem,
            "sem_match_revit": sem_match_revit,
            "sem_match_classificacao": sem_match_classificacao,
            "esquadrias_por_grupo": esquadrias_por_grupo}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Valida tipologias contra o Revit (opcional)")
    p.add_argument("--unidades", type=Path, required=True)
    p.add_argument("--revit", type=Path, required=True)
    p.add_argument("--tol", type=float, default=TOL_AREA_PADRAO)
    args = p.parse_args()
    unidades = json.loads(args.unidades.read_text(encoding="utf-8"))
    rev = json.loads(args.revit.read_text(encoding="utf-8"))
    revit_unidades = rev.get("unidades", rev) if isinstance(rev, dict) else rev
    print(json.dumps(validar(unidades, revit_unidades, tol_area=args.tol),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
