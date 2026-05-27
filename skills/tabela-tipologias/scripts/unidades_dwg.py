"""CLI: extrai contagem de esquadrias por unidade do DWG.

Uso:
    python unidades_dwg.py --dwg arquivo.dwg
    python unidades_dwg.py --dwg arquivo.dwg --listar-layers   # inspecionar layers
    python unidades_dwg.py --dwg arquivo.dwg --label-layer A-AREA-IDEN \\
        --janela-layers A-GLAZ,A-GLAZ-IDEN                      # adaptar por projeto

Os nomes de layer variam de projeto pra projeto. Se a contagem vier vazia/estranha,
rode --listar-layers primeiro e ajuste --label-layer / --janela-layers.
"""
import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    p = argparse.ArgumentParser(description="Extrai contagem de esquadrias por unidade do DWG.")
    p.add_argument("--dwg", required=True, help="Caminho para o arquivo DWG")
    p.add_argument("--listar-layers", action="store_true",
                   help="So lista os layers do DWG (e a contagem de entidades) e sai.")
    p.add_argument("--label-layer", default=None,
                   help="Layer dos numeros de unidade (default AIA: A-AREA-IDEN).")
    p.add_argument("--janela-layers", default=None,
                   help="Layers de esquadria separados por virgula (default: A-GLAZ,A-GLAZ-IDEN).")
    args = p.parse_args(argv)

    scripts_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(scripts_dir))
    import ler_dwg as L

    if args.listar_layers:
        layers = L.listar_layers(args.dwg)
        json.dump(layers, sys.stdout, ensure_ascii=False, indent=2)
        return 0

    kwargs = {}
    if args.label_layer:
        kwargs["label_layer"] = args.label_layer
    if args.janela_layers:
        kwargs["janela_layers"] = tuple(s.strip() for s in args.janela_layers.split(",") if s.strip())

    extraidos = L.ler_dwg(args.dwg, **kwargs)
    contagem = extraidos.contagem_por_unidade()
    json.dump(contagem, sys.stdout, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
