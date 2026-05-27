"""Faz upsert de um Spot no dashboard/data/orcamentos.js (window.ORCAMENTOS).

Le o orcamentos.js existente (se houver), substitui/adiciona o Spot pelo slug
e reescreve o arquivo. NUNCA toca tipologias.js.

Uso:
  python gerar_dashboard_js.py \
    --orcamentos-js dashboard/data/orcamentos.js \
    --spot "Natal Spot" --codigo 6953 --slug natal-spot \
    --estilo Clean --consolidado-url "https://docs.google.com/.../edit" \
    --memoriais tmp/memoriais.json \
    --memorial-urls tmp/memorial_urls.json \
    --gerado-em 2026-05-27
"""
import argparse
import json
import sys
from pathlib import Path

_PREFIXO = "window.ORCAMENTOS ="
_CABECALHO = "// dashboard/data/orcamentos.js -- reescrito pela skill orcamento-decor.\n"


def parsear_js(texto: str) -> dict:
    t = (texto or "").strip()
    if not t:
        return {"index": [], "spots": {}}
    linhas = [ln for ln in t.splitlines() if not ln.strip().startswith("//")]
    t = "\n".join(linhas).strip()
    if t.startswith(_PREFIXO):
        t = t[len(_PREFIXO):].strip()
    if t.endswith(";"):
        t = t[:-1].strip()
    if not t:
        return {"index": [], "spots": {}}
    return json.loads(t)


def serializar_js(orcamentos: dict) -> str:
    corpo = json.dumps(orcamentos, ensure_ascii=False, indent=2)
    return f"{_CABECALHO}{_PREFIXO} {corpo};\n"


def construir_entrada(
    spot: str, codigo: str, slug: str, estilo: str,
    consolidado_url: str, memoriais: dict,
    memorial_urls: dict, gerado_em: str,
) -> tuple[dict, dict]:
    lista = memoriais.get("memoriais", [])
    tipologias = [
        {
            "tipologia": m["tipologia"],
            "descricao": m["descricao"],
            "custo": m["total_geral"],
            "memorial_url": memorial_urls.get(m["tipologia"], "#"),
        }
        for m in lista
    ]
    index_entry = {
        "spot": spot, "codigo": str(codigo), "slug": slug,
        "estilo": estilo, "pacote": "Plus", "gerado_em": gerado_em,
        "total_tipologias": len(tipologias),
        "consolidado_url": consolidado_url,
    }
    spot_entry = {
        "spot": spot, "estilo": estilo, "pacote": "Plus",
        "consolidado_url": consolidado_url,
        "tipologias": tipologias,
    }
    return index_entry, spot_entry


def upsert_spot(orcamentos: dict, slug: str, index_entry: dict, spot_entry: dict) -> dict:
    index = [e for e in orcamentos.get("index", []) if e.get("slug") != slug]
    index.append(index_entry)
    spots = dict(orcamentos.get("spots", {}))
    spots[slug] = spot_entry
    return {"index": index, "spots": spots}


def main() -> None:
    p = argparse.ArgumentParser(description="Upsert de Spot em orcamentos.js")
    p.add_argument("--orcamentos-js", type=Path, required=True)
    p.add_argument("--spot", required=True)
    p.add_argument("--codigo", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--estilo", required=True)
    p.add_argument("--consolidado-url", required=True)
    p.add_argument("--memoriais", type=Path, required=True)
    p.add_argument("--memorial-urls", type=Path, required=True)
    p.add_argument("--gerado-em", required=True)
    args = p.parse_args()

    memoriais = json.loads(args.memoriais.read_text(encoding="utf-8"))
    memorial_urls = json.loads(args.memorial_urls.read_text(encoding="utf-8"))

    atual = parsear_js(args.orcamentos_js.read_text(encoding="utf-8")) \
        if args.orcamentos_js.exists() else {"index": [], "spots": {}}

    idx, sp = construir_entrada(
        spot=args.spot, codigo=args.codigo, slug=args.slug, estilo=args.estilo,
        consolidado_url=args.consolidado_url, memoriais=memoriais,
        memorial_urls=memorial_urls, gerado_em=args.gerado_em)

    novo = upsert_spot(atual, args.slug, idx, sp)
    args.orcamentos_js.write_text(serializar_js(novo), encoding="utf-8")
    print(f"orcamentos.js atualizado: {args.slug} ({len(sp['tipologias'])} tipologias)")


if __name__ == "__main__":
    main()
