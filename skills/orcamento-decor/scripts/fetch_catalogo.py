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
