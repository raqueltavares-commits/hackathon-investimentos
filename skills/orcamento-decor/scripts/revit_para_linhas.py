"""Transforma blocos do Revit (type_name + quantidade) em LinhaMemorial.

A skill (agente) coleta os blocos via MCP Revit-SZI — `ai_element_filter(category="OST_...",
visible_in_view=True)` (+ `get_element_properties` p/ família) — e monta um JSON:

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
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import LinhaMemorial

REGRAS_PADRAO_PATH = Path(__file__).parent.parent / "references/depara-revit.json"

# Categoria do Revit -> categoria do orçamento. ISTO generaliza entre projetos
# (independe dos nomes dos blocos, que mudam a cada Spot). Aceita o nome OST
# (OST_Furniture) ou o rótulo simples (Furniture / Mobiliário).
MAP_CATEGORIA_REVIT = {
    "furniture": "MOBILIÁRIO", "ost_furniture": "MOBILIÁRIO", "mobiliário": "MOBILIÁRIO",
    "furnituresystems": "MOBILIÁRIO", "ost_furnituresystems": "MOBILIÁRIO",
    "casework": "MARCENARIA", "ost_casework": "MARCENARIA", "marcenaria": "MARCENARIA",
    "lightingfixtures": "ILUMINAÇÃO", "ost_lightingfixtures": "ILUMINAÇÃO", "iluminação": "ILUMINAÇÃO",
    "plumbingfixtures": "METAIS E INOX", "ost_plumbingfixtures": "METAIS E INOX",
    "planting": "PAISAGISMO", "ost_planting": "PAISAGISMO", "paisagismo": "PAISAGISMO",
    "entourage": "PAISAGISMO", "ost_entourage": "PAISAGISMO",
    "specialityequipment": "ELETROS", "ost_specialityequipment": "ELETROS",
    "electricalfixtures": "ELETROS", "ost_electricalfixtures": "ELETROS",
    "signage": "SINALIZAÇÃO", "ost_signage": "SINALIZAÇÃO",
}


def _norm(s: str) -> str:
    """minúsculas + sem acento, pra casar substring de forma robusta."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def limpar_nome(type_name: str) -> str:
    """Tira o ruído de TypeName do Revit. Ex.:
    'Único:3432869 : Bancada 06:Único:3432869' -> 'Bancada 06'.
    Sem ':' (a maioria dos nomes legíveis), devolve o texto inteiro."""
    s = type_name.strip()
    if ":" not in s:
        return s
    partes = [p.strip() for p in s.split(":")]
    bons = [p for p in partes
            if p and _norm(p) != "unico" and not re.fullmatch(r"[\d\s.]+", p)]
    return max(bons, key=len) if bons else s


def _carregar_regras(caminho=None) -> list[dict]:
    p = Path(caminho) if caminho else REGRAS_PADRAO_PATH
    return json.loads(p.read_text(encoding="utf-8"))


REGRAS_PADRAO = _carregar_regras()


def casar_regra(type_name: str, regras: list[dict], family: str = "") -> dict | None:
    """Primeira regra cujo `match` (normalizado) é substring do type_name OU da família.
    A família ajuda quando o type_name é só a cor (ex: 'Cinza', 'Marfim'). None se nenhuma."""
    alvo = f"{_norm(type_name)} || {_norm(family)}"
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
    """Consolida blocos por (categoria, item), somando quantidade.

    Project-agnostic: a categoria vem da CATEGORIA DO REVIT (`categoria_revit`),
    não dos nomes de bloco (que mudam a cada Spot). O `depara-revit.json` é só uma
    camada opcional de apelidos/preço. Devolve:
      {"linhas": [...], "nao_mapeados": [...], "a_precificar": [...]}
    - nao_mapeados: blocos sem categoria reconhecida (Revit nem de-para) -> "A REVISAR".
    - a_precificar: itens que saíram com valor 0 (precisam de preço/confirmação)."""
    regras = regras if regras is not None else REGRAS_PADRAO
    acc: dict[tuple, LinhaMemorial] = {}
    ordem: list[tuple] = []
    nao_mapeados: list[str] = []

    for b in blocos:
        type_name = b.get("type_name", "")
        family = b.get("family", "")
        qtd = int(b.get("qtd", 0) or 0)
        cat_revit = MAP_CATEGORIA_REVIT.get(_norm(b.get("categoria_revit", "")))

        regra = casar_regra(type_name, regras, family)
        if regra:  # apelido conhecido: usa item/categoria/código do de-para
            categoria, item, codigo = regra["categoria"], regra["item"], regra.get("codigo", "")
        else:      # generaliza: categoria do Revit + nome do próprio bloco
            item = limpar_nome(type_name)
            if family and _norm(family) not in _norm(type_name):
                item = f"{item} ({family})"
            codigo = ""
            if cat_revit:
                categoria = cat_revit
            else:
                categoria = "A REVISAR"
                if item not in nao_mapeados:
                    nao_mapeados.append(item)

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

    linhas = [acc[k] for k in ordem]
    a_precificar = [l.item for l in linhas if l.valor_unitario == 0.0]
    return {"linhas": linhas, "nao_mapeados": nao_mapeados, "a_precificar": a_precificar}


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
        "a_precificar": res["a_precificar"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
