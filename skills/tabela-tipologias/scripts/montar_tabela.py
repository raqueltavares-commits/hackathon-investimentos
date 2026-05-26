"""Agrupa unidades classificadas em tipologias, valida totais e gera CSV.

Uso (runtime da skill):
    python montar_tabela.py --total 96 < unidades.json

Entrada: JSON (stdin) = lista de unidades classificadas.
Saída: JSON (stdout) = {"tipologias": [...], "validacao": {...}, "csv": "..."}.
"""
import csv
import io
import json
import sys
from collections import defaultdict
