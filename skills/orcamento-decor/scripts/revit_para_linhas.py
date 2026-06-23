"""Transforma blocos do Revit (type_name + quantidade) em LinhaMemorial.

A skill (agente) coleta os blocos via Revit MCP — `get_elements_by_category(cat, view)`
+ `get_element_types_for_elementids` — e monta um JSON:

  {"ambiente": "Rooftop", "blocos": [{"type_name": "freijó", "qtd": 2}, ...]}

Este script casa cada type_name com uma regra de de-para (substring, case-insensitive),
consolida quantidades por item e puxa preço/cor/link do catálogo (quando há `codigo`).
Tipos não reconhecidos NÃO somem: viram linha "A REVISAR" (valor 0) e entram em
`nao_mapeados` pra revisão da Raquel. Cor/acabamento final vem dos renders (passo à parte).

Uso:
  python revit_para_linhas.py --blocos tmp/blocos.json --produtos tmp/produtos.json \
    --ambiente Rooftop > tmp/linhas_rooftop.json
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import LinhaMemorial

REGRAS_PADRAO_PATH = Path(__file__).parent.parent / "references/depara-revit.json"


def _norm(s: str) -> str:
    """minúsculas + sem acento, pra casar substring de forma robusta."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def _carregar_regras(caminho=None) -> list[dict]:
    p = Path(caminho) if caminho else REGRAS_PADRAO_PATH
    return json.loads(p.read_text(encoding="utf-8"))


REGRAS_PADRAO = _carregar_regras()


def casar_regra(type_name: str, regras: list[dict]) -> dict | None:
    """Primeira regra cujo `match` (normalizado) é substring do type_name. None se nenhuma."""
    alvo = _norm(type_name)
    for r in regras:
        if _norm(r["match"]) in alvo:
            return r
    return None


def _preco_cor_link(codigo: str, produtos: dict) -> tuple[float, str, str]:
    p = produtos.get(codigo) if codigo else None
    if not p:
        return 0.0, "", ""
    return (float(p.get("valor_unitario") or 0.0),
            p.get("cor_acabamento", "") or "", p.get("link", "") or "")


def blocos_para_linhas(blocos: list[dict], produtos: dict,
                       ambiente: str = "", regras: list[dict] | None = None) -> dict:
    """Consolida blocos por (categoria, item), somando quantidade. Devolve
    {"linhas": [LinhaMemorial], "nao_mapeados": [type_name, ...]}."""
    regras = regras if regras is not None else REGRAS_PADRAO
    acc: dict[tuple, LinhaMemorial] = {}
    ordem: list[tuple] = []
    nao_mapeados: list[str] = []

    for b in blocos:
        type_name = b.get("type_name", "")
        qtd = int(b.get("qtd", 0) or 0)
        regra = casar_regra(type_name, regras)
        if regra:
            categoria, item, codigo = regra["categoria"], regra["item"], regra.get("codigo", "")
        else:
            categoria, item, codigo = "A REVISAR", type_name, ""
            if type_name not in nao_mapeados:
                nao_mapeados.append(type_name)

        chave = (categoria, item)
        if chave in acc:
            acc[chave].quantidade += qtd
        else:
            valor, cor, link = _preco_cor_link(codigo, produtos)
            acc[chave] = LinhaMemorial(
                categoria=categoria, item=item, quantidade=qtd, valor_unitario=valor,
                ambiente=ambiente, referencia=link or codigo,
                cor_acabamento=cor or "A definir (ver render)",
            )
            ordem.append(chave)

    return {"linhas": [acc[k] for k in ordem], "nao_mapeados": nao_mapeados}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Converte blocos do Revit em linhas de memorial")
    p.add_argument("--blocos", type=Path, required=True)
    p.add_argument("--produtos", type=Path)
    p.add_argument("--ambiente", default="")
    p.add_argument("--regras", type=Path, help="de-para Revit (default: references/depara-revit.json)")
    args = p.parse_args()

    payload = json.loads(args.blocos.read_text(encoding="utf-8"))
    blocos = payload.get("blocos", payload) if isinstance(payload, dict) else payload
    ambiente = args.ambiente or (payload.get("ambiente", "") if isinstance(payload, dict) else "")
    produtos = json.loads(args.produtos.read_text(encoding="utf-8")) if args.produtos else {}
    regras = _carregar_regras(args.regras) if args.regras else REGRAS_PADRAO

    res = blocos_para_linhas(blocos, produtos, ambiente=ambiente, regras=regras)
    out = {
        "ambiente": ambiente,
        "linhas": [
            {"categoria": l.categoria, "ambiente": l.ambiente, "item": l.item,
             "quantidade": l.quantidade, "valor_unitario": l.valor_unitario,
             "cor_acabamento": l.cor_acabamento, "referencia": l.referencia}
            for l in res["linhas"]
        ],
        "nao_mapeados": res["nao_mapeados"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
