"""Parseia CSV do db002_produtos (exportado do Drive) -> dict[str, Produto].

Uso:
  python ler_catalogo.py --csv caminho/db002.csv > produtos.json
  cat db002.csv | python ler_catalogo.py > produtos.json
  python ler_catalogo.py --csv db002.csv --col-codigo Ref --col-valor_unitario Price
"""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from modelos import Produto

COLUNAS_PADRAO = {
    "codigo":         ["codigo", "código", "cod", "id", "referencia", "ref", "sku"],
    "nome":           ["nome", "descricao", "descrição", "produto", "item", "name"],
    "categoria":      ["categoria", "categoria_produto", "tipo", "grupo", "category"],
    "valor_unitario": ["valor_unitario", "valor unitário", "preco", "preço", "price",
                       "valor", "vl_unitario"],
    "unidade":        ["unidade", "un", "unid", "unit"],
}


def _encontrar_coluna(headers: list[str], alternativas: list[str]) -> str | None:
    hl = [h.lower().strip() for h in headers]
    for alt in alternativas:
        if alt.lower() in hl:
            return headers[hl.index(alt.lower())]
    return None


def _parse_valor(s: str) -> float:
    if not s or s.strip() in ("", "-", "N/A", "n/a"):
        return 0.0
    s = s.strip().lstrip("R$").strip().strip('"').strip()
    # Formato pt-BR: "1.234,56" → ponto é milhar, vírgula é decimal
    # Formato en-US: "1234.56" → ponto é decimal
    # Heurística: se houver vírgula, tratar como pt-BR
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    # else: ponto já é decimal (en-US), não mexer
    try:
        return float(s)
    except ValueError:
        return 0.0


def parsear_csv(
    texto_csv: str,
    mapeamento: dict[str, str] | None = None,
) -> dict[str, Produto]:
    reader = csv.DictReader(io.StringIO(texto_csv))
    headers = list(reader.fieldnames or [])

    mapa = dict(mapeamento or {})
    for campo, alternativas in COLUNAS_PADRAO.items():
        if campo not in mapa:
            col = _encontrar_coluna(headers, alternativas)
            if col:
                mapa[campo] = col

    faltando = [c for c in ("codigo", "nome", "categoria", "valor_unitario")
                if c not in mapa]
    if faltando:
        raise ValueError(
            f"Colunas não encontradas: {faltando}. "
            f"Disponíveis: {headers}. "
            f"Use --col-<campo> para mapear manualmente."
        )

    produtos: dict[str, Produto] = {}
    for row in reader:
        codigo = row.get(mapa["codigo"], "").strip()
        if not codigo:
            continue
        col_unidade = mapa.get("unidade", "__NA__")
        produtos[codigo] = Produto(
            codigo=codigo,
            nome=row.get(mapa["nome"], "").strip(),
            categoria=row.get(mapa["categoria"], "").strip().upper(),
            valor_unitario=_parse_valor(row.get(mapa["valor_unitario"], "")),
            unidade=row.get(col_unidade, "un").strip() or "un",
        )
    return produtos


def main() -> None:
    p = argparse.ArgumentParser(description="Parseia CSV do db002_produtos -> JSON")
    p.add_argument("--csv", type=Path, help="Caminho do CSV (default: stdin)")
    for campo in COLUNAS_PADRAO:
        p.add_argument(f"--col-{campo}", dest=f"col_{campo}",
                       help=f"Nome da coluna para '{campo}' (auto-detectado se omitido)")
    args = p.parse_args()

    texto = args.csv.read_text(encoding="utf-8-sig") if args.csv else sys.stdin.read()
    mapeamento = {
        campo: getattr(args, f"col_{campo}")
        for campo in COLUNAS_PADRAO
        if getattr(args, f"col_{campo}") is not None
    }

    try:
        produtos = parsear_csv(texto, mapeamento or None)
        saida = {
            k: {"nome": v.nome, "categoria": v.categoria,
                "valor_unitario": v.valor_unitario, "unidade": v.unidade}
            for k, v in produtos.items()
        }
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    except ValueError as e:
        print(json.dumps({"erro": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
