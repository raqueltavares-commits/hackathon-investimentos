"""Monta um .xlsx multi-aba (uma aba por tipologia + Resumo) a partir do JSON de montar_orcamento.

Uso:
  python montar_orcamento.py ... > memoriais.json
  python gerar_xlsx.py --memoriais memoriais.json --spot "Bonito Spot" --saida saida.xlsx
"""
import argparse
import json
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

NAVY = "FF000C3C"
bold = Font(bold=True)
bold_white = Font(bold=True, color="FFFFFFFF")
navy_fill = PatternFill("solid", fgColor=NAVY)


def _aba(ws, rows, cabecalho=None):
    """Renderiza uma aba no layout de 11 colunas. `cabecalho` (opcional) é uma
    lista de linhas (Empreendimento/Endereço/CEP) impressa antes da matriz.
    `rows[0]` é o título e `rows[1]` é o cabeçalho de colunas."""
    offset = 0
    if cabecalho:
        for linha in cabecalho:
            ws.append(linha)
            ws.cell(row=ws.max_row, column=1).font = bold
        ws.append([])
        offset = len(cabecalho) + 1
    for r in rows:
        ws.append(r)
    for c in ws[offset + 2]:  # rows[1] = cabeçalho de colunas
        c.font = bold_white
        c.fill = navy_fill
    larguras = {"A": 16, "B": 16, "C": 42, "D": 20, "E": 18, "F": 6,
                "G": 24, "H": 15, "I": 15, "J": 12, "K": 16}
    for col, w in larguras.items():
        ws.column_dimensions[col].width = w


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--memoriais", type=Path, required=True)
    p.add_argument("--spot", required=True)
    p.add_argument("--saida", type=Path, required=True)
    p.add_argument("--endereco", default="", help="Endereço do empreendimento (cabeçalho)")
    p.add_argument("--cep", default="", help="CEP do empreendimento (cabeçalho)")
    args = p.parse_args()

    data = json.loads(args.memoriais.read_text(encoding="utf-8"))
    wb = Workbook()

    # Cabeçalho Empreendimento/Endereço/CEP, repetido em cada aba (referência de frete).
    cabecalho = [[f"Empreendimento: {args.spot}"]]
    if args.endereco:
        cabecalho.append([f"Endereço: {args.endereco}"])
    if args.cep:
        cabecalho.append([f"CEP: {args.cep}"])

    ws = wb.active
    ws.title = "Resumo Unidades"
    ws.append([f"{args.spot} — Orçamento Decor (Plus) · Unidades"])
    ws["A1"].font = Font(bold=True, size=13)
    if args.endereco or args.cep:
        ws.append([f"{args.endereco}  ·  CEP {args.cep}".strip(" ·")])
    ws.append([])
    # Unidades NÃO levam Taxa Adm (só área comum) — o total já reflete isso.
    ws.append(["TIPOLOGIA", "DESCRIÇÃO", "CUSTO ESTIMADO (sem jacuzzi)", "COM JACUZZI"])
    head_row = ws.max_row
    for c in ws[head_row]:
        c.font = bold_white
        c.fill = navy_fill
    for m in data["memoriais"]:
        ws.append([m["tipologia"], m["descricao"], m["total_geral"], m["total_com_jacuzzi"]])
        ws.cell(row=ws.max_row, column=3).number_format = 'R$ #,##0.00'
        ws.cell(row=ws.max_row, column=4).number_format = 'R$ #,##0.00'
    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 32
    ws.column_dimensions["C"].width = 26
    ws.column_dimensions["D"].width = 18

    for m in data["memoriais"]:
        aba = wb.create_sheet(title=f"Tipologia {m['tipologia']}")
        _aba(aba, m["rows"], cabecalho=cabecalho)

    wb.save(args.saida)
    print(f"xlsx salvo: {args.saida} | abas: {wb.sheetnames}")


if __name__ == "__main__":
    main()
