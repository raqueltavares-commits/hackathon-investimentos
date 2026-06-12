"""Lê o catálogo de preços ao vivo do Supabase (app seazone-decor-interno).

Substitui o download do CSV do Drive. Resolve a anon key a partir do bundle de
produção (RLS libera leitura anon), consulta a tabela `produto` pelos códigos do
de-para e devolve JSON no mesmo formato que ler_catalogo.py produzia:

  { "<codigo-item>": {"nome","categoria","valor_unitario","unidade"}, ... }

Uso:
  python fetch_catalogo.py > tmp/produtos.json
  python fetch_catalogo.py --depara skills/orcamento-decor/references/depara-catalogo.json
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

SITE_URL = "https://seazone-decor-interno.seazone.properties"
SUPABASE_URL = "https://cjbsotszriddpadznhvk.supabase.co"
DEPARA_PADRAO = Path(__file__).parent.parent / "references/depara-catalogo.json"

_RE_BUNDLE = re.compile(r"assets/[^\"']+\.js")
_RE_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")


def extrair_bundle_path(html: str) -> str | None:
    m = _RE_BUNDLE.search(html or "")
    return m.group(0) if m else None


def extrair_anon_key(js: str) -> str | None:
    m = _RE_JWT.search(js or "")
    return m.group(0) if m else None


def normalizar(s):
    """Corrige double-encoding (UTF-8 lido como latin1): 'Ã§' -> 'ç'."""
    if not isinstance(s, str):
        return s
    if any(c in s for c in ("Ã", "Â", "�")):
        try:
            return s.encode("latin1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return s
    return s


def carregar_depara(caminho) -> dict:
    p = Path(caminho) if caminho else DEPARA_PADRAO
    return json.loads(p.read_text(encoding="utf-8"))


def parsear_resposta(json_text: str, depara: dict) -> dict:
    """Recebe linhas da API (list[dict]) + de-para (codigo-item -> produto.codigo)
    e devolve {codigo-item: {nome, categoria, valor_unitario, unidade}}."""
    linhas = json.loads(json_text)
    # reverso: produto.codigo -> [codigos-item]
    reverso: dict[int, list[str]] = {}
    for cod_item, cod_base in depara.items():
        reverso.setdefault(cod_base, []).append(cod_item)

    produtos: dict[str, dict] = {}
    for row in linhas:
        cod_base = row.get("codigo")
        for cod_item in reverso.get(cod_base, []):
            produtos[cod_item] = {
                "nome": normalizar(row.get("nome", "")),
                "categoria": row.get("subcategoria_codigo", "") or "",
                "valor_unitario": float(row.get("valor") or 0.0),
                "unidade": "un",
            }
    return produtos


class CatalogoError(RuntimeError):
    pass


def _http_get(url: str, headers: dict | None = None) -> str:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def buscar_catalogo(depara: dict, http_get=_http_get) -> dict:
    html = http_get(SITE_URL + "/")
    bundle = extrair_bundle_path(html)
    if not bundle:
        raise CatalogoError("Bundle JS não encontrado no HTML de produção.")
    js = http_get(f"{SITE_URL}/{bundle}")
    key = extrair_anon_key(js)
    if not key:
        raise CatalogoError("Anon key não encontrada no bundle.")
    codigos = ",".join(str(c) for c in sorted(set(depara.values())))
    url = (f"{SUPABASE_URL}/rest/v1/produto"
           f"?select=codigo,nome,valor,subcategoria_codigo&codigo=in.({codigos})")
    corpo = http_get(url, headers={"apikey": key, "Authorization": f"Bearer {key}"})
    return parsear_resposta(corpo, depara)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Lê o catálogo de preços do Supabase")
    p.add_argument("--depara", help="Caminho do de-para (default: references/depara-catalogo.json)")
    args = p.parse_args()
    try:
        depara = carregar_depara(args.depara)
        produtos = buscar_catalogo(depara)
        print(json.dumps(produtos, ensure_ascii=False, indent=2))
    except (CatalogoError, OSError, ValueError) as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
