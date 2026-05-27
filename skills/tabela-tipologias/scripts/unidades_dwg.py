"""CLI: extrai contagem de esquadrias por unidade do DWG.

Uso:
    python unidades_dwg.py --dwg caminho/para/arquivo.dwg
"""
import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(description="Extrai contagem de esquadrias por unidade do DWG.")
    p.add_argument("--dwg", required=True, help="Caminho para o arquivo DWG")
    args = p.parse_args(argv)

    scripts_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(scripts_dir))
    from ler_dwg import ler_dwg

    extraidos = ler_dwg(args.dwg)
    contagem = extraidos.contagem_por_unidade()
    json.dump(contagem, sys.stdout, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
