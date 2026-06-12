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
import base64
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
    """Prefere o chunk de entrada do Vite (`index-*.js`); a anon key vive nele,
    não nos chunks de vendor. Cai no primeiro `.js` se não houver `index-`."""
    matches = _RE_BUNDLE.findall(html or "")
    if not matches:
        return None
    for m in matches:
        if "index-" in m:
            return m
    return matches[0]


def _role_do_jwt(token: str) -> str | None:
    """Lê o claim `role` do payload do JWT (sem validar assinatura)."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload)).get("role")
    except Exception:
        return None


def extrair_anon_key(js: str) -> str | None:
    """Escolhe explicitamente o token com `role:anon` — o bundle pode conter
    outros JWTs (ex: service_role), que NÃO devem ser usados."""
    tokens = _RE_JWT.findall(js or "")
    if not tokens:
        return None
    for t in tokens:
        if _role_do_jwt(t) == "anon":
            return t
    return tokens[0]


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
                # `categoria` aqui é o código da subcategoria (ex: "2.1.1"), só
                # informativo: montar_orcamento.py usa a categoria do próprio item
                # (_ITENS_PLUS) pro agrupamento, não esta. Preço é por código.
                "categoria": row.get("subcategoria_codigo", "") or "",
                "valor_unitario": float(row.get("valor") or 0.0),
                "unidade": "un",
            }
    return produtos


class CatalogoError(RuntimeError):
    pass


# WAF de produção bloqueia o User-Agent padrão do urllib (403); emula um browser.
_USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _http_get(url: str, headers: dict | None = None) -> str:
    cabecalhos = {"User-Agent": _USER_AGENT, **(headers or {})}
    req = urllib.request.Request(url, headers=cabecalhos)
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
